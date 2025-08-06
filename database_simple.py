"""
Simple Database module for EVE Trading Market Analysis Tool.
Uses SQLite directly for better Python 3.13 compatibility.
"""

import sqlite3
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import json
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class SimpleDatabaseManager:
    """Simple database manager using SQLite directly."""
    
    def __init__(self, db_path: str = "eve_trading.db"):
        """
        Initialize the database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()
        logger.info(f"Database initialized: {db_path}")
    
    def init_database(self):
        """Initialize database tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create market_orders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    type_id INTEGER NOT NULL,
                    location_id INTEGER NOT NULL,
                    region_id INTEGER NOT NULL,
                    price REAL NOT NULL,
                    volume_remain INTEGER NOT NULL,
                    volume_total INTEGER NOT NULL,
                    order_type TEXT NOT NULL,
                    issued TEXT NOT NULL,
                    duration INTEGER NOT NULL,
                    is_buy_order INTEGER NOT NULL,
                    min_volume INTEGER NOT NULL,
                    range TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create market_analysis table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS market_analysis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_id INTEGER NOT NULL,
                    analysis_date TEXT NOT NULL,
                    total_orders INTEGER NOT NULL,
                    avg_price REAL NOT NULL,
                    median_price REAL NOT NULL,
                    min_price REAL NOT NULL,
                    max_price REAL NOT NULL,
                    total_volume INTEGER NOT NULL,
                    unique_locations INTEGER NOT NULL,
                    price_std REAL,
                    volume_weighted_avg_price REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create discovered_items table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS discovered_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    subcategory TEXT NOT NULL,
                    volume_24h INTEGER NOT NULL,
                    avg_price REAL NOT NULL,
                    profit_margin REAL NOT NULL,
                    demand_score REAL NOT NULL,
                    supply_score REAL NOT NULL,
                    volatility_score REAL NOT NULL,
                    competition_score REAL NOT NULL,
                    overall_score REAL NOT NULL,
                    market_activity TEXT NOT NULL,
                    description TEXT,
                    discovered_at TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_type_id ON market_orders(type_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_location_id ON market_orders(location_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_issued ON market_orders(issued)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_price ON market_orders(price)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_order_type ON market_orders(order_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_analysis_type_date ON market_analysis(type_id, analysis_date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_discovered_type_id ON discovered_items(type_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_discovered_score ON discovered_items(overall_score)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_discovered_category ON discovered_items(category)')
            
            conn.commit()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access
        try:
            yield conn
        finally:
            conn.close()
    
    def store_market_orders(self, orders: List[Dict[str, Any]], type_id: int) -> int:
        """
        Store market orders in the database.
        
        Args:
            orders: List of market order dictionaries
            type_id: The item type ID
            
        Returns:
            Number of orders stored
        """
        stored_count = 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            for order_data in orders:
                try:
                    cursor.execute('''
                        INSERT INTO market_orders (
                            order_id, type_id, location_id, region_id, price,
                            volume_remain, volume_total, order_type, issued,
                            duration, is_buy_order, min_volume, range
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        order_data['order_id'],
                        type_id,
                        order_data['location_id'],
                        order_data.get('region_id', 10000002),
                        order_data['price'],
                        order_data['volume_remain'],
                        order_data['volume_total'],
                        order_data['order_type'],
                        order_data['issued'],
                        order_data['duration'],
                        order_data['is_buy_order'],
                        order_data.get('min_volume', 1),
                        order_data.get('range', 'region')
                    ))
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing order {order_data.get('order_id', 'unknown')}: {e}")
                    continue
            
            conn.commit()
            logger.info(f"Stored {stored_count} market orders for type_id {type_id}")
        
        return stored_count
    
    def get_market_orders(self, type_id: int, limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieve market orders for a specific item.
        
        Args:
            type_id: The item type ID
            limit: Maximum number of orders to retrieve
            
        Returns:
            DataFrame with market orders
        """
        with self.get_connection() as conn:
            query = '''
                SELECT * FROM market_orders 
                WHERE type_id = ? 
                ORDER BY issued DESC
            '''
            
            if limit:
                query += f' LIMIT {limit}'
            
            df = pd.read_sql_query(query, conn, params=(type_id,))
            return df
    
    def get_historical_orders(self, type_id: int, days: int = 30) -> pd.DataFrame:
        """
        Get historical market orders for trend analysis.
        
        Args:
            type_id: The item type ID
            days: Number of days to look back
            
        Returns:
            DataFrame with historical orders
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        with self.get_connection() as conn:
            query = '''
                SELECT order_id, price, volume_remain, location_id, issued, order_type
                FROM market_orders 
                WHERE type_id = ? AND issued >= ?
                ORDER BY issued DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(type_id, cutoff_date))
            return df
    
    def store_market_analysis(self, analysis_data: Dict[str, Any], type_id: int) -> bool:
        """
        Store computed market analysis.
        
        Args:
            analysis_data: Dictionary with analysis results
            type_id: The item type ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO market_analysis (
                        type_id, analysis_date, total_orders, avg_price, median_price,
                        min_price, max_price, total_volume, unique_locations,
                        price_std, volume_weighted_avg_price
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    type_id,
                    datetime.utcnow().isoformat(),
                    analysis_data.get('total_orders', 0),
                    analysis_data.get('avg_price', 0.0),
                    analysis_data.get('median_price', 0.0),
                    analysis_data.get('min_price', 0.0),
                    analysis_data.get('max_price', 0.0),
                    analysis_data.get('total_volume', 0),
                    analysis_data.get('unique_locations', 0),
                    analysis_data.get('price_std', 0.0),
                    analysis_data.get('volume_weighted_avg_price', 0.0)
                ))
                
                conn.commit()
                logger.info(f"Stored market analysis for type_id {type_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error storing market analysis: {e}")
            return False
    
    def get_market_trends(self, type_id: int, days: int = 30) -> pd.DataFrame:
        """
        Get market trends over time.
        
        Args:
            type_id: The item type ID
            days: Number of days to analyze
            
        Returns:
            DataFrame with trend data
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        with self.get_connection() as conn:
            query = '''
                SELECT * FROM market_analysis 
                WHERE type_id = ? AND analysis_date >= ?
                ORDER BY analysis_date
            '''
            
            df = pd.read_sql_query(query, conn, params=(type_id, cutoff_date))
            return df
    
    def get_top_items_by_volume(self, limit: int = 10) -> pd.DataFrame:
        """
        Get top items by trading volume.
        
        Args:
            limit: Number of items to return
            
        Returns:
            DataFrame with top items
        """
        with self.get_connection() as conn:
            query = '''
                SELECT 
                    CAST(type_id AS INTEGER) as type_id,
                    CAST(total_volume AS INTEGER) as total_volume,
                    CAST(avg_price AS REAL) as avg_price,
                    CAST(total_orders AS INTEGER) as total_orders,
                    analysis_date
                FROM market_analysis 
                WHERE analysis_date = (
                    SELECT MAX(analysis_date) 
                    FROM market_analysis ma2 
                    WHERE ma2.type_id = market_analysis.type_id
                )
                ORDER BY total_volume DESC 
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(limit,))
            return df
    
    def cleanup_old_data(self, days: int = 90) -> int:
        """
        Clean up old market orders to prevent database bloat.
        
        Args:
            days: Remove orders older than this many days
            
        Returns:
            Number of records deleted
        """
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM market_orders WHERE issued < ?', (cutoff_date,))
            deleted_count = cursor.rowcount
            conn.commit()
            
            logger.info(f"Cleaned up {deleted_count} old market orders")
            return deleted_count
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get counts
            cursor.execute('SELECT COUNT(*) FROM market_orders')
            total_orders = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM market_analysis')
            total_analyses = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(DISTINCT type_id) FROM market_orders')
            unique_items = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute('SELECT MIN(issued), MAX(issued) FROM market_orders')
            date_range = cursor.fetchone()
            oldest_order = date_range[0] if date_range[0] else None
            newest_order = date_range[1] if date_range[1] else None
            
            return {
                'total_orders': total_orders,
                'total_analyses': total_analyses,
                'unique_items': unique_items,
                'oldest_order': oldest_order,
                'newest_order': newest_order
            }
    
    async def store_discovered_item(self, item_data: Dict[str, Any]) -> bool:
        """
        Store discovered item in the database.
        
        Args:
            item_data: Dictionary containing item information
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO discovered_items (
                        type_id, name, category, subcategory, volume_24h,
                        avg_price, profit_margin, demand_score, supply_score,
                        volatility_score, competition_score, overall_score,
                        market_activity, description, discovered_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item_data['type_id'],
                    item_data['name'],
                    item_data['category'],
                    item_data['subcategory'],
                    item_data['volume_24h'],
                    item_data['avg_price'],
                    item_data['profit_margin'],
                    item_data['demand_score'],
                    item_data['supply_score'],
                    item_data['volatility_score'],
                    item_data['competition_score'],
                    item_data['overall_score'],
                    item_data['market_activity'],
                    item_data.get('description', ''),
                    item_data['discovered_at']
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error storing discovered item {item_data.get('type_id', 'unknown')}: {e}")
            return False
    
    def get_top_discovered_items(self, limit: int = 50, min_score: float = 0.5) -> pd.DataFrame:
        """
        Get top discovered items by overall score.
        
        Args:
            limit: Maximum number of items to return
            min_score: Minimum overall score threshold
            
        Returns:
            DataFrame with discovered items
        """
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT * FROM discovered_items 
                    WHERE overall_score >= ? 
                    ORDER BY overall_score DESC 
                    LIMIT ?
                '''
                
                df = pd.read_sql_query(query, conn, params=(min_score, limit))
                return df
                
        except Exception as e:
            logger.error(f"Error getting discovered items: {e}")
            return pd.DataFrame()
    
    def get_discovered_items_by_category(self, category: str, limit: int = 20) -> pd.DataFrame:
        """
        Get discovered items by category.
        
        Args:
            category: Item category
            limit: Maximum number of items to return
            
        Returns:
            DataFrame with discovered items
        """
        try:
            with self.get_connection() as conn:
                query = '''
                    SELECT * FROM discovered_items 
                    WHERE category = ? 
                    ORDER BY overall_score DESC 
                    LIMIT ?
                '''
                
                df = pd.read_sql_query(query, conn, params=(category, limit))
                return df
                
        except Exception as e:
            logger.error(f"Error getting discovered items by category: {e}")
            return pd.DataFrame()

def main():
    """Demo function to test the database."""
    db_manager = SimpleDatabaseManager()
    print("Simple Database manager initialized successfully!")
    print("Use this class in your main script for data persistence.")

if __name__ == "__main__":
    main() 
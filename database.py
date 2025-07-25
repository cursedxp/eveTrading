"""
Database module for EVE Trading Market Analysis Tool.
Provides data persistence, historical analysis, and efficient data management.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Optional, Any
import pandas as pd
import logging
from datetime import datetime, timedelta
import os
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database setup
Base = declarative_base()

class MarketOrder(Base):
    """Model for storing market order data."""
    __tablename__ = 'market_orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, nullable=False)
    type_id = Column(Integer, nullable=False)
    location_id = Column(Integer, nullable=False)
    region_id = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    volume_remain = Column(Integer, nullable=False)
    volume_total = Column(Integer, nullable=False)
    order_type = Column(String(10), nullable=False)  # 'sell' or 'buy'
    issued = Column(DateTime, nullable=False)
    duration = Column(Integer, nullable=False)
    is_buy_order = Column(Integer, nullable=False)  # 0 or 1
    min_volume = Column(Integer, nullable=False)
    range = Column(String(20), nullable=False)
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_type_id', 'type_id'),
        Index('idx_location_id', 'location_id'),
        Index('idx_issued', 'issued'),
        Index('idx_price', 'price'),
        Index('idx_order_type', 'order_type'),
    )

class ItemInfo(Base):
    """Model for storing item information."""
    __tablename__ = 'item_info'
    
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    category = Column(String(100), nullable=True)
    group = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketAnalysis(Base):
    """Model for storing computed market analysis."""
    __tablename__ = 'market_analysis'
    
    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, nullable=False)
    analysis_date = Column(DateTime, nullable=False)
    total_orders = Column(Integer, nullable=False)
    avg_price = Column(Float, nullable=False)
    median_price = Column(Float, nullable=False)
    min_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=False)
    total_volume = Column(Integer, nullable=False)
    unique_locations = Column(Integer, nullable=False)
    price_std = Column(Float, nullable=True)
    volume_weighted_avg_price = Column(Float, nullable=True)
    
    __table_args__ = (
        Index('idx_type_id_date', 'type_id', 'analysis_date'),
    )

class DatabaseManager:
    """Manages database operations for the EVE Trading application."""
    
    def __init__(self, db_url: str = "sqlite:///eve_trading.db"):
        """
        Initialize the database manager.
        
        Args:
            db_url: SQLAlchemy database URL
        """
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        logger.info(f"Database initialized: {db_url}")
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
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
        
        with self.get_session() as session:
            for order_data in orders:
                try:
                    # Convert issued string to datetime
                    issued_str = order_data.get('issued', '')
                    issued_dt = datetime.fromisoformat(issued_str.replace('Z', '+00:00'))
                    
                    # Create market order object
                    market_order = MarketOrder(
                        order_id=order_data['order_id'],
                        type_id=type_id,
                        location_id=order_data['location_id'],
                        region_id=order_data.get('region_id', 10000002),  # Default to Forge
                        price=order_data['price'],
                        volume_remain=order_data['volume_remain'],
                        volume_total=order_data['volume_total'],
                        order_type=order_data['order_type'],
                        issued=issued_dt,
                        duration=order_data['duration'],
                        is_buy_order=order_data['is_buy_order'],
                        min_volume=order_data.get('min_volume', 1),
                        range=order_data.get('range', 'region')
                    )
                    
                    session.add(market_order)
                    stored_count += 1
                    
                except Exception as e:
                    logger.error(f"Error storing order {order_data.get('order_id', 'unknown')}: {e}")
                    continue
            
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
        with self.get_session() as session:
            query = session.query(MarketOrder).filter(MarketOrder.type_id == type_id)
            
            if limit:
                query = query.limit(limit)
            
            orders = query.all()
            
            # Convert to DataFrame
            data = []
            for order in orders:
                data.append({
                    'order_id': order.order_id,
                    'type_id': order.type_id,
                    'location_id': order.location_id,
                    'region_id': order.region_id,
                    'price': order.price,
                    'volume_remain': order.volume_remain,
                    'volume_total': order.volume_total,
                    'order_type': order.order_type,
                    'issued': order.issued,
                    'duration': order.duration,
                    'is_buy_order': order.is_buy_order,
                    'min_volume': order.min_volume,
                    'range': order.range
                })
            
            return pd.DataFrame(data)
    
    def get_historical_orders(self, type_id: int, days: int = 30) -> pd.DataFrame:
        """
        Get historical market orders for trend analysis.
        
        Args:
            type_id: The item type ID
            days: Number of days to look back
            
        Returns:
            DataFrame with historical orders
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            query = session.query(MarketOrder).filter(
                MarketOrder.type_id == type_id,
                MarketOrder.issued >= cutoff_date
            ).order_by(MarketOrder.issued.desc())
            
            orders = query.all()
            
            data = []
            for order in orders:
                data.append({
                    'order_id': order.order_id,
                    'price': order.price,
                    'volume_remain': order.volume_remain,
                    'location_id': order.location_id,
                    'issued': order.issued,
                    'order_type': order.order_type
                })
            
            return pd.DataFrame(data)
    
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
            with self.get_session() as session:
                analysis = MarketAnalysis(
                    type_id=type_id,
                    analysis_date=datetime.utcnow(),
                    total_orders=analysis_data.get('total_orders', 0),
                    avg_price=analysis_data.get('avg_price', 0.0),
                    median_price=analysis_data.get('median_price', 0.0),
                    min_price=analysis_data.get('min_price', 0.0),
                    max_price=analysis_data.get('max_price', 0.0),
                    total_volume=analysis_data.get('total_volume', 0),
                    unique_locations=analysis_data.get('unique_locations', 0),
                    price_std=analysis_data.get('price_std', 0.0),
                    volume_weighted_avg_price=analysis_data.get('volume_weighted_avg_price', 0.0)
                )
                
                session.add(analysis)
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
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            query = session.query(MarketAnalysis).filter(
                MarketAnalysis.type_id == type_id,
                MarketAnalysis.analysis_date >= cutoff_date
            ).order_by(MarketAnalysis.analysis_date)
            
            analyses = query.all()
            
            data = []
            for analysis in analyses:
                data.append({
                    'analysis_date': analysis.analysis_date,
                    'total_orders': analysis.total_orders,
                    'avg_price': analysis.avg_price,
                    'median_price': analysis.median_price,
                    'min_price': analysis.min_price,
                    'max_price': analysis.max_price,
                    'total_volume': analysis.total_volume,
                    'unique_locations': analysis.unique_locations,
                    'price_std': analysis.price_std,
                    'volume_weighted_avg_price': analysis.volume_weighted_avg_price
                })
            
            return pd.DataFrame(data)
    
    def get_top_items_by_volume(self, limit: int = 10) -> pd.DataFrame:
        """
        Get top items by trading volume.
        
        Args:
            limit: Number of items to return
            
        Returns:
            DataFrame with top items
        """
        with self.get_session() as session:
            # Get the most recent analysis for each type_id
            query = session.query(MarketAnalysis).from_self().join(
                session.query(MarketAnalysis.type_id, 
                            MarketAnalysis.analysis_date.label('max_date'))
                .group_by(MarketAnalysis.type_id)
                .subquery(),
                MarketAnalysis.type_id == MarketAnalysis.type_id,
                MarketAnalysis.analysis_date == MarketAnalysis.analysis_date
            ).order_by(MarketAnalysis.total_volume.desc()).limit(limit)
            
            analyses = query.all()
            
            data = []
            for analysis in analyses:
                data.append({
                    'type_id': analysis.type_id,
                    'total_volume': analysis.total_volume,
                    'avg_price': analysis.avg_price,
                    'total_orders': analysis.total_orders,
                    'analysis_date': analysis.analysis_date
                })
            
            return pd.DataFrame(data)
    
    def cleanup_old_data(self, days: int = 90) -> int:
        """
        Clean up old market orders to prevent database bloat.
        
        Args:
            days: Remove orders older than this many days
            
        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        with self.get_session() as session:
            deleted_count = session.query(MarketOrder).filter(
                MarketOrder.issued < cutoff_date
            ).delete()
            
            logger.info(f"Cleaned up {deleted_count} old market orders")
            return deleted_count
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        with self.get_session() as session:
            total_orders = session.query(MarketOrder).count()
            total_analyses = session.query(MarketAnalysis).count()
            unique_items = session.query(MarketOrder.type_id).distinct().count()
            
            # Get date range
            oldest_order = session.query(MarketOrder.issued).order_by(MarketOrder.issued.asc()).first()
            newest_order = session.query(MarketOrder.issued).order_by(MarketOrder.issued.desc()).first()
            
            return {
                'total_orders': total_orders,
                'total_analyses': total_analyses,
                'unique_items': unique_items,
                'oldest_order': oldest_order[0] if oldest_order else None,
                'newest_order': newest_order[0] if newest_order else None
            }

def main():
    """Demo function to test the database."""
    db_manager = DatabaseManager()
    print("Database manager initialized successfully!")
    print("Use this class in your main script for data persistence.")

if __name__ == "__main__":
    main() 
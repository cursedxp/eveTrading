"""
Multi-Item Data Fetcher - Fetch market data for multiple items simultaneously
Uses the profitable item finder results to fetch data for the best trading opportunities
"""

import asyncio
import aiohttp
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import logging
from database_simple import SimpleDatabaseManager
from profitable_item_finder import ProfitableItemFinder
from eve_items_database import get_item_names

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiItemFetcher:
    def __init__(self, region_id: int = 10000002):  # The Forge
        self.region_id = region_id
        self.session = None
        self.db = SimpleDatabaseManager()
        self.item_names = get_item_names()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_market_orders(self, type_id: int) -> List[Dict]:
        """Fetch market orders for a specific item"""
        try:
            # Fetch both buy and sell orders
            sell_url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type=sell&type_id={type_id}"
            buy_url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type=buy&type_id={type_id}"
            
            async with self.session.get(sell_url) as sell_response, self.session.get(buy_url) as buy_response:
                sell_orders = await sell_response.json() if sell_response.status == 200 else []
                buy_orders = await buy_response.json() if buy_response.status == 200 else []
                
                # Add order type and item info to each order
                for order in sell_orders:
                    order['order_type'] = 'sell'
                    order['item_name'] = self.item_names.get(type_id, f"Item {type_id}")
                
                for order in buy_orders:
                    order['order_type'] = 'buy'
                    order['item_name'] = self.item_names.get(type_id, f"Item {type_id}")
                
                return sell_orders + buy_orders
        except Exception as e:
            logger.error(f"Error fetching market orders for type_id {type_id}: {e}")
            return []
    
    async def fetch_item_data(self, type_id: int, item_name: str) -> bool:
        """Fetch and store market data for a single item"""
        try:
            logger.info(f"Fetching data for {item_name} (ID: {type_id})...")
            orders = await self.fetch_market_orders(type_id)
            
            if not orders:
                logger.warning(f"No market data found for {item_name}")
                return False
            
            # Store orders in database
            try:
                stored_count = self.db.store_market_orders(orders, type_id)
                logger.info(f"Stored {stored_count} orders for {item_name}")
                return stored_count > 0
            except Exception as e:
                logger.error(f"Error storing orders for {item_name}: {e}")
                return False
            
        except Exception as e:
            logger.error(f"Error fetching data for {item_name}: {e}")
            return False
    
    async def fetch_profitable_items_data(self, max_items: int = 10) -> Dict[str, int]:
        """Fetch data for the most profitable items"""
        logger.info("Finding profitable items and fetching their data...")
        
        # Use profitable item finder to get best items
        async with ProfitableItemFinder() as finder:
            analyses = await finder.find_profitable_items(max_items=max_items)
            
            # Get the top items by score
            top_items = sorted(analyses, key=lambda x: x.overall_score, reverse=True)[:max_items]
            
            logger.info(f"Found {len(top_items)} profitable items to fetch data for")
            
            # Fetch data for each item
            results = {}
            for analysis in top_items:
                success = await self.fetch_item_data(analysis.type_id, analysis.item_name)
                results[analysis.item_name] = 1 if success else 0
            
            return results
    
    async def fetch_custom_items_data(self, type_ids: List[int]) -> Dict[str, int]:
        """Fetch data for custom list of items"""
        logger.info(f"Fetching data for {len(type_ids)} custom items...")
        
        results = {}
        for type_id in type_ids:
            item_name = self.item_names.get(type_id, f"Item {type_id}")
            success = await self.fetch_item_data(type_id, item_name)
            results[item_name] = 1 if success else 0
        
        return results
    
    def get_database_summary(self) -> Dict:
        """Get summary of stored data"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get total orders
            cursor.execute("SELECT COUNT(*) FROM market_orders")
            total_orders = cursor.fetchone()[0]
            
            # Get unique items
            cursor.execute("SELECT COUNT(DISTINCT type_id) FROM market_orders")
            unique_items = cursor.fetchone()[0]
            
            # Get items with most orders
            cursor.execute("""
                SELECT type_id, COUNT(*) as order_count, 
                       SUM(volume_remain) as total_volume
                FROM market_orders 
                GROUP BY type_id 
                ORDER BY order_count DESC 
                LIMIT 5
            """)
            top_items = cursor.fetchall()
            
            return {
                'total_orders': total_orders,
                'unique_items': unique_items,
                'top_items': top_items
            }

async def main():
    """Main function to run the multi-item fetcher"""
    print("📡 EVE Multi-Item Data Fetcher")
    print("="*50)
    
    async with MultiItemFetcher() as fetcher:
        # Option 1: Fetch data for profitable items
        print("\n🔍 Fetching data for profitable items...")
        results = await fetcher.fetch_profitable_items_data(max_items=8)
        
        print("\n📊 Fetch Results:")
        for item_name, success in results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {item_name}: {status}")
        
        # Option 2: Fetch data for specific items
        print("\n📡 Fetching data for specific items...")
        specific_items = [34, 35, 36, 37, 38, 39, 40]  # Basic minerals
        specific_results = await fetcher.fetch_custom_items_data(specific_items)
        
        print("\n📊 Specific Items Results:")
        for item_name, success in specific_results.items():
            status = "✅ Success" if success else "❌ Failed"
            print(f"  {item_name}: {status}")
        
        # Show database summary
        print("\n🗄️ Database Summary:")
        summary = fetcher.get_database_summary()
        print(f"  Total Orders: {summary['total_orders']:,}")
        print(f"  Unique Items: {summary['unique_items']}")
        
        print("\n📈 Top Items by Order Count:")
        for type_id, count, volume in summary['top_items']:
            item_name = fetcher.item_names.get(type_id, f"Item {type_id}")
            print(f"  {item_name}: {count:,} orders, {volume:,} volume")

if __name__ == "__main__":
    asyncio.run(main()) 
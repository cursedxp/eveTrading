"""
Dynamic Item Discovery System - Uses EVE ESI API to find profitable items
Automatically discovers and updates the database with profitable trading opportunities
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import json
from database_simple import SimpleDatabaseManager
from eve_items_database import EVE_ITEMS, get_item_names

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MarketItem:
    type_id: int
    name: str
    category: str
    volume_24h: int
    avg_price: float
    price_change_24h: float
    profit_margin: float
    score: float

class DynamicItemDiscovery:
    def __init__(self, region_id: int = 10000002):  # The Forge
        self.region_id = region_id
        self.session = None
        self.db = SimpleDatabaseManager()
        self.discovered_items = set()
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_market_groups(self) -> List[Dict]:
        """Get all market groups from ESI"""
        try:
            url = "https://esi.evetech.net/latest/markets/groups/?datasource=tranquility"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return []
        except Exception as e:
            logger.error(f"Error fetching market groups: {e}")
            return []
    
    async def get_market_group_items(self, group_id: int) -> List[Dict]:
        """Get items in a specific market group"""
        try:
            url = f"https://esi.evetech.net/latest/markets/groups/{group_id}/?datasource=tranquility"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('types', [])
                return []
        except Exception as e:
            logger.error(f"Error fetching market group {group_id}: {e}")
            return []
    
    async def get_item_info(self, type_id: int) -> Optional[Dict]:
        """Get item information from ESI"""
        try:
            url = f"https://esi.evetech.net/latest/universe/types/{type_id}/?datasource=tranquility"
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logger.error(f"Error fetching item info for {type_id}: {e}")
            return None
    
    async def get_market_orders_for_item(self, type_id: int) -> List[Dict]:
        """Get market orders for a specific item"""
        try:
            sell_url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type=sell&type_id={type_id}"
            buy_url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type=buy&type_id={type_id}"
            
            async with self.session.get(sell_url) as sell_response, self.session.get(buy_url) as buy_response:
                sell_orders = await sell_response.json() if sell_response.status == 200 else []
                buy_orders = await buy_response.json() if buy_response.status == 200 else []
                
                # Add order type
                for order in sell_orders:
                    order['order_type'] = 'sell'
                for order in buy_orders:
                    order['order_type'] = 'buy'
                
                return sell_orders + buy_orders
        except Exception as e:
            logger.error(f"Error fetching market orders for {type_id}: {e}")
            return []
    
    async def get_item_name(self, type_id: int) -> str:
        """Get item name from ESI API using type ID"""
        try:
            url = f"https://esi.evetech.net/latest/universe/types/{type_id}/?datasource=tranquility"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('name', f'Item_{type_id}')
                else:
                    logger.warning(f"Failed to get item name for type_id {type_id}: {response.status}")
                    return f'Item_{type_id}'
        except Exception as e:
            logger.error(f"Error fetching item name for {type_id}: {e}")
            return f'Item_{type_id}'
    
    async def calculate_profitability_score(self, orders: List[Dict]) -> Optional[MarketItem]:
        """Calculate profitability score for an item"""
        if not orders:
            return None
        
        # Separate buy and sell orders
        sell_orders = [o for o in orders if o['order_type'] == 'sell']
        buy_orders = [o for o in orders if o['order_type'] == 'buy']
        
        if not sell_orders or not buy_orders:
            return None
        
        # Calculate metrics
        current_buy_price = min(o['price'] for o in sell_orders)  # Lowest sell order (best price to buy)
        current_sell_price = max(o['price'] for o in buy_orders)  # Highest buy order (best price to sell)
        avg_price = (current_sell_price + current_buy_price) / 2
        
        # Calculate volume
        volume_24h = sum(o.get('volume_remain', 0) for o in orders)
        
        # Calculate profit margin
        profit_margin = (current_sell_price - current_buy_price) / current_buy_price if current_buy_price > 0 else 0
        
        # VALIDATION: Sanity check for unrealistic profit margins
        if profit_margin > 0.5:  # 50% profit margin
            logger.warning(f"Unrealistic profit margin detected: {profit_margin:.2%} for type_id {orders[0]['type_id']}")
            profit_margin = min(profit_margin, 0.5)
        
        if profit_margin < 0:
            logger.warning(f"Negative profit margin detected: {profit_margin:.2%} for type_id {orders[0]['type_id']}")
            profit_margin = 0
        
        # Calculate price change (simplified)
        price_change_24h = 0.05  # Placeholder - would need historical data
        
        # Calculate overall score
        score = (
            profit_margin * 0.4 +
            min(1.0, volume_24h / 10000) * 0.3 +  # Volume score
            min(1.0, abs(price_change_24h) * 10) * 0.3  # Volatility score
        )
        
        # Get real item name from ESI API
        type_id = orders[0]['type_id']
        item_name = await self.get_item_name(type_id)
        
        return MarketItem(
            type_id=type_id,
            name=item_name,
            category="Unknown",
            volume_24h=volume_24h,
            avg_price=avg_price,
            price_change_24h=price_change_24h,
            profit_margin=profit_margin,
            score=score
        )
    
    async def discover_profitable_items(self, min_score: float = 0.5, max_items: int = 50) -> List[MarketItem]:
        """Discover profitable items using ESI API"""
        logger.info("Starting dynamic item discovery...")
        
        # Get market groups
        market_groups = await self.get_market_groups()
        logger.info(f"Found {len(market_groups)} market groups")
        
        # Focus on high-volume groups (minerals, ships, modules, etc.)
        priority_groups = [
            1032,  # Minerals
            1033,  # Advanced Materials
            1034,  # Ships
            1035,  # Ship Equipment
            1036,  # Ship Modifications
            1037,  # Ship Modifications
            1038,  # Ship Modifications
            1039,  # Ship Modifications
            1040,  # Ship Modifications
            1041,  # Ship Modifications
            1042,  # Ship Modifications
            1043,  # Ship Modifications
            1044,  # Ship Modifications
            1045,  # Ship Modifications
            1046,  # Ship Modifications
            1047,  # Ship Modifications
            1048,  # Ship Modifications
            1049,  # Ship Modifications
            1050,  # Ship Modifications
            1051,  # Ship Modifications
            1052,  # Ship Modifications
            1053,  # Ship Modifications
            1054,  # Ship Modifications
            1055,  # Ship Modifications
            1056,  # Ship Modifications
            1057,  # Ship Modifications
            1058,  # Ship Modifications
            1059,  # Ship Modifications
            1060,  # Ship Modifications
            1061,  # Ship Modifications
            1062,  # Ship Modifications
            1063,  # Ship Modifications
            1064,  # Ship Modifications
            1065,  # Ship Modifications
            1066,  # Ship Modifications
            1067,  # Ship Modifications
            1068,  # Ship Modifications
            1069,  # Ship Modifications
            1070,  # Ship Modifications
            1071,  # Ship Modifications
            1072,  # Ship Modifications
            1073,  # Ship Modifications
            1074,  # Ship Modifications
            1075,  # Ship Modifications
            1076,  # Ship Modifications
            1077,  # Ship Modifications
            1078,  # Ship Modifications
            1079,  # Ship Modifications
            1080,  # Ship Modifications
            1081,  # Ship Modifications
            1082,  # Ship Modifications
            1083,  # Ship Modifications
            1084,  # Ship Modifications
            1085,  # Ship Modifications
            1086,  # Ship Modifications
            1087,  # Ship Modifications
            1088,  # Ship Modifications
            1089,  # Ship Modifications
            1090,  # Ship Modifications
            1091,  # Ship Modifications
            1092,  # Ship Modifications
            1093,  # Ship Modifications
            1094,  # Ship Modifications
            1095,  # Ship Modifications
            1096,  # Ship Modifications
            1097,  # Ship Modifications
            1098,  # Ship Modifications
            1099,  # Ship Modifications
            1100,  # Ship Modifications
        ]
        
        profitable_items = []
        discovered_count = 0
        
        for group_id in priority_groups[:20]:  # Limit to first 20 groups for performance
            try:
                logger.info(f"Analyzing market group {group_id}...")
                type_ids = await self.get_market_group_items(group_id)
                
                for type_id in type_ids[:10]:  # Limit to first 10 items per group
                    if type_id in self.discovered_items:
                        continue
                    
                    # Get market orders
                    orders = await self.get_market_orders_for_item(type_id)
                    if not orders:
                        continue
                    
                    # Calculate profitability
                    market_item = await self.calculate_profitability_score(orders)
                    if market_item and market_item.score >= min_score:
                        profitable_items.append(market_item)
                        self.discovered_items.add(type_id)
                        discovered_count += 1
                        
                        if discovered_count >= max_items:
                            break
                
                if discovered_count >= max_items:
                    break
                    
            except Exception as e:
                logger.error(f"Error analyzing market group {group_id}: {e}")
                continue
        
        # Sort by score
        profitable_items.sort(key=lambda x: x.score, reverse=True)
        
        logger.info(f"Discovered {len(profitable_items)} profitable items")
        return profitable_items
    
    async def update_database_with_discovered_items(self, items: List[MarketItem]) -> Dict[str, int]:
        """Update database with discovered items"""
        logger.info(f"Updating database with {len(items)} discovered items...")
        
        results = {}
        for item in items:
            try:
                # First, store the discovered item metadata
                item_data = {
                    'type_id': item.type_id,
                    'name': item.name,
                    'category': item.category,
                    'subcategory': "Unknown",
                    'volume_24h': item.volume_24h,
                    'avg_price': item.avg_price,
                    'profit_margin': item.profit_margin,
                    'demand_score': 0.5,  # Default values
                    'supply_score': 0.5,
                    'volatility_score': 0.5,
                    'competition_score': 0.5,
                    'overall_score': item.score,
                    'market_activity': "Active",
                    'description': f"Dynamically discovered profitable item",
                    'discovered_at': datetime.now().isoformat()
                }
                await self.db.store_discovered_item(item_data)
                
                # Then, get market orders and store in database
                orders = await self.get_market_orders_for_item(item.type_id)
                if orders:
                    stored_count = self.db.store_market_orders(orders, item.type_id)
                    results[f"Item {item.type_id}"] = stored_count
                    logger.info(f"Stored {stored_count} orders for item {item.type_id} (Score: {item.score:.2f})")
                else:
                    results[f"Item {item.type_id}"] = 0
                    
            except Exception as e:
                logger.error(f"Error updating database for item {item.type_id}: {e}")
                results[f"Item {item.type_id}"] = 0
        
        return results
    
    async def export_discovered_items_to_mongodb(self, items: List[MarketItem]):
        """Export discovered items directly to MongoDB"""
        try:
            from mongodb_service import get_mongodb_service
            mongo_service = get_mongodb_service()
            collection = mongo_service.db["discovered_items"]
            
            documents = []
            for item in items:
                doc = {
                    '_id': item.type_id,  # Use type_id as unique identifier
                    'type_id': item.type_id,
                    'name': item.name,
                    'category': item.category,
                    'volume_24h': item.volume_24h,
                    'avg_price': item.avg_price,
                    'price_change_24h': item.price_change_24h,
                    'profit_margin': item.profit_margin,
                    'overall_score': item.score,
                    'discovered_at': datetime.now(),
                    'last_updated': datetime.now()
                }
                documents.append(doc)
            
            # Use upsert to update existing items or insert new ones
            for doc in documents:
                collection.replace_one({'_id': doc['_id']}, doc, upsert=True)
            
            mongo_service.close()
            logger.info(f"Discovered items exported to MongoDB: {len(documents)} items")
            
        except Exception as e:
            logger.error(f"Error exporting to MongoDB: {e}")
            # Fallback to database storage
            await self.update_database_with_discovered_items(items)
    
    def display_discovered_items(self, items: List[MarketItem], top_n: int = 20):
        """Display discovered items in a formatted table"""
        if not items:
            print("No profitable items discovered.")
            return
        
        print("\n" + "="*100)
        print("DISCOVERED PROFITABLE ITEMS")
        print("="*100)
        print(f"{'Type ID':<10} {'Name':<25} {'Category':<15} {'Volume':<10} {'Price':<10} {'Profit %':<10} {'Score':<8}")
        print("-"*100)
        
        for item in items[:top_n]:
            print(f"{item.type_id:<10} {item.name:<25} {item.category:<15} {item.volume_24h:<10} "
                  f"{item.avg_price:<9.2f} {item.profit_margin*100:<9.1f}% {item.score:<7.2f}")
        
        print("-"*100)
        print(f"Discovered {len(items)} items. Showing top {min(top_n, len(items))} results.")

async def main():
    """Main function to run dynamic item discovery"""
    print("🔍 EVE Dynamic Item Discovery System")
    print("="*50)
    
    async with DynamicItemDiscovery() as discoverer:
        # Discover profitable items
        items = await discoverer.discover_profitable_items(min_score=0.4, max_items=30)
        
        if items:
            # Display results
            discoverer.display_discovered_items(items, top_n=15)
            
            # Export results to MongoDB (no more JSON files)
            await discoverer.export_discovered_items_to_mongodb(items)
            
            # Also update the main database
            results = await discoverer.update_database_with_discovered_items(items)
            
            print("\n📊 Database Update Results:")
            for item_name, count in results.items():
                status = "✅ Success" if count > 0 else "❌ Failed"
                print(f"  {item_name}: {count} orders ({status})")
        else:
            print("No profitable items discovered.")

if __name__ == "__main__":
    asyncio.run(main()) 
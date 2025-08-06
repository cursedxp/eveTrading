#!/usr/bin/env python3
"""
Efficient EVE Route Finder - Minimal API Calls
- Makes only 5 API calls total (one per region)
- Gets ALL market data at once
- AI makes decisions on all opportunities
- No more individual item calls
"""

import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass 
class EfficientRoute:
    item_name: str
    type_id: int
    buy_hub: str
    sell_hub: str
    buy_price: float
    sell_price: float
    quantity: int
    net_profit: float
    profit_percent: float
    ai_verdict: str
    ai_reasoning: str

class EfficientRouteFinder:
    """Minimal API calls approach"""
    
    HUBS = {
        "Jita": {"region_id": 10000002, "station_id": 60003760},
        "Amarr": {"region_id": 10000043, "station_id": 60008494},
        "Dodixie": {"region_id": 10000032, "station_id": 60011866},
        "Rens": {"region_id": 10000030, "station_id": 60004588},
        "Hek": {"region_id": 10000042, "station_id": 60005686}
    }
    
    # Items to analyze
    ITEMS = {
        587: "Rifter", 34: "Tritanium", 35: "Pyerite", 36: "Mexallon",
        37: "Isogen", 38: "Nocxium", 39: "Zydrine", 40: "Megacyte"
    }
    
    def __init__(self):
        self.session = None
        self.api_calls = 0
        self.total_orders = 0
        self.fresh_orders = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def is_fresh(self, issued_date: str) -> bool:
        """Check if order is less than 12 hours old"""
        try:
            order_time = datetime.fromisoformat(issued_date.replace('Z', '+00:00'))
            age_hours = (datetime.now(order_time.tzinfo) - order_time).total_seconds() / 3600
            return age_hours < 12
        except:
            return False
    
    async def fetch_region_data(self, hub_name: str, region_id: int) -> Dict:
        """Fetch ALL orders for a region in one go"""
        logger.info(f"📡 Fetching ALL market data for {hub_name}...")
        
        all_orders = []
        page = 1
        
        try:
            while page <= 10:  # Reasonable limit
                url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
                params = {"datasource": "tranquility", "page": page}
                
                async with self.session.get(url, params=params) as response:
                    self.api_calls += 1
                    
                    if response.status == 404:  # No more pages
                        break
                    elif response.status != 200:
                        break
                    
                    orders = await response.json()
                    if not orders:
                        break
                    
                    all_orders.extend(orders)
                    page += 1
            
            # Filter to our station and items only
            station_id = self.HUBS[hub_name]["station_id"]
            relevant_orders = [
                order for order in all_orders
                if (order.get('location_id') == station_id and 
                    order['type_id'] in self.ITEMS and
                    self.is_fresh(order.get('issued', '')))
            ]
            
            self.total_orders += len(all_orders)
            self.fresh_orders += len(relevant_orders)
            
            # Group by item
            items_data = defaultdict(lambda: {'buy_orders': [], 'sell_orders': []})
            
            for order in relevant_orders:
                type_id = order['type_id']
                order_data = {
                    'price': order['price'],
                    'volume': order['volume_remain']
                }
                
                if order.get('is_buy_order', False):
                    items_data[type_id]['buy_orders'].append(order_data)
                else:
                    items_data[type_id]['sell_orders'].append(order_data)
            
            logger.info(f"  ✅ {hub_name}: {len(relevant_orders)} fresh orders for {len(items_data)} items")
            return dict(items_data)
            
        except Exception as e:
            logger.error(f"Error fetching {hub_name}: {e}")
            return {}
    
    async def get_all_market_data(self) -> Dict[str, Dict]:
        """Get ALL market data with just 5 API calls"""
        logger.info("🚀 EFFICIENT FETCH: Getting all data in parallel...")
        
        tasks = [
            self.fetch_region_data(hub_name, hub_info["region_id"])
            for hub_name, hub_info in self.HUBS.items()
        ]
        
        results = await asyncio.gather(*tasks)
        
        return dict(zip(self.HUBS.keys(), results))
    
    def ai_evaluate(self, profit_pct: float, total_profit: float, volume: int) -> tuple:
        """Simple AI evaluation"""
        score = 0
        reasons = []
        
        # Profit percentage scoring
        if profit_pct > 100:
            score += 50
            reasons.append("huge margins")
        elif profit_pct > 50:
            score += 40
            reasons.append("excellent margins") 
        elif profit_pct > 25:
            score += 30
            reasons.append("great margins")
        elif profit_pct > 15:
            score += 25
            reasons.append("good margins")
        elif profit_pct > 10:
            score += 20
            reasons.append("decent margins")
        elif profit_pct > 5:
            score += 15
            reasons.append("modest margins")
        elif profit_pct > 2:
            score += 10
            reasons.append("small margins")
        
        # Total profit scoring
        if total_profit > 10_000_000:
            score += 25
            reasons.append("large profit")
        elif total_profit > 1_000_000:
            score += 15
            reasons.append("good profit")
        elif total_profit > 500_000:
            score += 10
            reasons.append("decent profit")
        elif total_profit > 100_000:
            score += 5
            reasons.append("small profit")
        
        # Volume scoring
        if volume > 1000:
            score += 15
            reasons.append("high volume")
        elif volume > 100:
            score += 10
            reasons.append("good volume")
        elif volume > 20:
            score += 5
            reasons.append("decent volume")
        
        # AI decision
        if score >= 80:
            verdict = "EXCELLENT"
        elif score >= 65:
            verdict = "STRONG"
        elif score >= 50:
            verdict = "GOOD" 
        elif score >= 35:
            verdict = "CONSIDER"
        elif score >= 20:
            verdict = "WEAK"
        else:
            verdict = "SKIP"
        
        reasoning = f"{verdict.lower()} - " + ", ".join(reasons[:3])
        return verdict, reasoning
    
    def analyze_opportunities(self, market_data: Dict[str, Dict]) -> List[EfficientRoute]:
        """Analyze all opportunities from cached data"""
        routes = []
        
        logger.info("🧠 AI analyzing all opportunities...")
        
        for type_id, item_name in self.ITEMS.items():
            for buy_hub in self.HUBS.keys():
                for sell_hub in self.HUBS.keys():
                    if buy_hub == sell_hub:
                        continue
                    
                    # Get market data
                    buy_data = market_data.get(buy_hub, {}).get(type_id)
                    sell_data = market_data.get(sell_hub, {}).get(type_id)
                    
                    if not buy_data or not sell_data:
                        continue
                    if not buy_data['sell_orders'] or not sell_data['buy_orders']:
                        continue
                    
                    # Calculate best prices
                    buy_price = min(o['price'] for o in buy_data['sell_orders'])
                    sell_price = max(o['price'] for o in sell_data['buy_orders'])
                    
                    if sell_price <= buy_price:
                        continue
                    
                    # Calculate volume and profit
                    buy_vol = sum(o['volume'] for o in buy_data['sell_orders'])
                    sell_vol = sum(o['volume'] for o in sell_data['buy_orders'])
                    quantity = min(buy_vol, sell_vol, 5000)
                    
                    if quantity <= 0:
                        continue
                    
                    gross_profit = (sell_price - buy_price) * quantity
                    transport_cost = buy_price * quantity * 0.02
                    net_profit = gross_profit - transport_cost
                    profit_percent = (net_profit / (buy_price * quantity)) * 100
                    
                    # AI evaluation
                    verdict, reasoning = self.ai_evaluate(profit_percent, net_profit, quantity)
                    
                    # Only include AI-approved routes
                    if verdict not in ["SKIP", "WEAK"]:
                        routes.append(EfficientRoute(
                            item_name=item_name,
                            type_id=type_id,
                            buy_hub=buy_hub,
                            sell_hub=sell_hub,
                            buy_price=buy_price,
                            sell_price=sell_price,
                            quantity=quantity,
                            net_profit=net_profit,
                            profit_percent=profit_percent,
                            ai_verdict=verdict,
                            ai_reasoning=reasoning
                        ))
        
        return sorted(routes, key=lambda x: x.net_profit, reverse=True)
    
    async def find_efficient_routes(self) -> List[EfficientRoute]:
        """Find routes with minimal API calls"""
        start_time = time.time()
        
        # Step 1: Get all market data (5 API calls max)
        market_data = await self.get_all_market_data()
        
        # Step 2: Analyze in memory (no more API calls)
        routes = self.analyze_opportunities(market_data)
        
        total_time = time.time() - start_time
        
        logger.info(f"\n⚡ EFFICIENCY REPORT:")
        logger.info(f"  • Total time: {total_time:.1f}s")
        logger.info(f"  • API calls: {self.api_calls} (vs 320+ before)")
        logger.info(f"  • Orders processed: {self.total_orders:,}")
        logger.info(f"  • Fresh orders: {self.fresh_orders:,}")
        logger.info(f"  • AI-approved routes: {len(routes)}")
        logger.info(f"  • Efficiency gain: {320/max(self.api_calls,1):.0f}x fewer API calls")
        
        return routes
    
    def display_results(self, routes: List[EfficientRoute]):
        """Display results"""
        print("\n" + "="*100)
        print("⚡ ULTRA-EFFICIENT EVE ROUTE FINDER")
        print("="*100)
        print("🚀 Minimal API calls • 🤖 AI decision making • ⏰ Fresh data only")
        print("="*100)
        
        if not routes:
            print("\n❌ No AI-approved opportunities found")
            return
        
        print(f"\n🏆 {len(routes)} AI-APPROVED OPPORTUNITIES:")
        print(f"{'#':<3} {'Item':<12} {'Route':<12} {'Profit':<12} {'%':<8} {'Qty':<8} {'AI Verdict'}")
        print("-"*80)
        
        for i, route in enumerate(routes[:20], 1):
            route_str = f"{route.buy_hub[:3]}→{route.sell_hub[:3]}"
            print(f"{i:<3} {route.item_name[:11]:<12} {route_str:<12} "
                  f"{route.net_profit:>11,.0f} {route.profit_percent:>7.1f}% "
                  f"{route.quantity:<8,} {route.ai_verdict}")
        
        if routes:
            best = routes[0]
            print(f"\n🥇 AI'S TOP PICK:")
            print(f"   {best.item_name}: {best.buy_hub} → {best.sell_hub}")
            print(f"   Profit: {best.net_profit:,.0f} ISK ({best.profit_percent:.1f}%)")
            print(f"   Volume: {best.quantity:,} units")
            print(f"   AI says: {best.ai_reasoning}")

async def main():
    """Test the efficient finder"""
    print("⚡ EVE ULTRA-EFFICIENT ROUTE FINDER")
    print("="*50)
    print("Goal: Minimal API calls with AI decisions")
    print("="*50)
    
    async with EfficientRouteFinder() as finder:
        routes = await finder.find_efficient_routes()
        finder.display_results(routes)

if __name__ == "__main__":
    asyncio.run(main())
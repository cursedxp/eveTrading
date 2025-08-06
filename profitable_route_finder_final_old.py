#!/usr/bin/env python3
"""
Final Optimized Profitable Route Finder
- Smart bulk processing with minimal API calls
- Real-time price data (no caching since prices change rapidly)
- Efficient batch analysis of all items
- AI decision making for human-like filtering
- Performance optimized for real-world usage
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import time
from collections import defaultdict
from database_simple import SimpleDatabaseManager
from mongodb_service import get_mongodb_service
# AI classes moved inline to avoid dependencies

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TraderProfile:
    """Represents a trader's preferences and constraints"""
    available_capital: float = 1_000_000_000  # 1B ISK
    max_cargo_capacity: float = 100_000  # m3
    preferred_profit_margin: float = 10.0  # %
    risk_tolerance: str = "medium"  # low, medium, high
    time_per_jump: int = 2  # minutes
    hourly_opportunity_cost: float = 50_000_000  # ISK/hour they could make doing other activities
    max_investment_per_item: float = 0.2  # 20% of capital max per item
    preferred_trade_volume: str = "medium"  # low, medium, high volume trades
    station_trading: bool = False  # Whether they prefer station trading
    experience_level: str = "intermediate"  # novice, intermediate, expert

class AITradingBrain:
    """Simplified AI system for route evaluation"""
    
    def __init__(self, trader_profile: TraderProfile):
        self.profile = trader_profile
        
        # Decision thresholds based on risk tolerance
        if self.profile.risk_tolerance == "low":
            self.thresholds = {
                "min_profit_percent": 15.0,
                "min_total_profit": 1_000_000,
                "max_risk_score": 30,
                "min_confidence": 0.7
            }
        elif self.profile.risk_tolerance == "high":
            self.thresholds = {
                "min_profit_percent": 5.0,
                "min_total_profit": 100_000,
                "max_risk_score": 70,
                "min_confidence": 0.4
            }
        else:  # medium
            self.thresholds = {
                "min_profit_percent": 10.0,
                "min_total_profit": 500_000,
                "max_risk_score": 50,
                "min_confidence": 0.6
            }

@dataclass
class OptimizedRoute:
    """Final optimized route with all analysis"""
    item_name: str
    type_id: int
    buy_hub: str
    sell_hub: str
    buy_price: float
    sell_price: float
    quantity: int
    gross_profit: float
    transport_cost: float
    net_profit: float
    profit_percent: float
    time_minutes: int
    isk_per_hour: float
    ai_score: float
    ai_verdict: str
    risk_assessment: str

class FinalOptimizedRouteFinder:
    """Final optimized route finder with best performance strategies"""
    
    # Major trade hubs
    HUBS = {
        "Jita": {"region_id": 10000002, "system_id": 30000142},
        "Amarr": {"region_id": 10000043, "system_id": 30002187},
        "Dodixie": {"region_id": 10000032, "system_id": 30002659},
        "Rens": {"region_id": 10000030, "system_id": 30002510},
        "Hek": {"region_id": 10000042, "system_id": 30002053}
    }
    
    # Travel data between hubs
    TRAVEL_DATA = {
        ("Jita", "Amarr"): {"jumps": 9, "minutes": 20, "cost_multiplier": 0.02},
        ("Jita", "Dodixie"): {"jumps": 15, "minutes": 32, "cost_multiplier": 0.03},
        ("Jita", "Rens"): {"jumps": 23, "minutes": 48, "cost_multiplier": 0.04},
        ("Jita", "Hek"): {"jumps": 25, "minutes": 52, "cost_multiplier": 0.05},
        ("Amarr", "Dodixie"): {"jumps": 17, "minutes": 36, "cost_multiplier": 0.025},
        ("Amarr", "Rens"): {"jumps": 28, "minutes": 58, "cost_multiplier": 0.035},
        ("Amarr", "Hek"): {"jumps": 30, "minutes": 62, "cost_multiplier": 0.045},
        ("Dodixie", "Rens"): {"jumps": 12, "minutes": 26, "cost_multiplier": 0.02},
        ("Dodixie", "Hek"): {"jumps": 18, "minutes": 38, "cost_multiplier": 0.03},
        ("Rens", "Hek"): {"jumps": 6, "minutes": 14, "cost_multiplier": 0.015}
    }
    
    def __init__(self, trader_profile: Optional[TraderProfile] = None):
        self.session = None
        self.mongo_service = None
        self.ai_brain = AITradingBrain(trader_profile or TraderProfile())
        self.db = SimpleDatabaseManager()
        
        # Performance tracking
        self.api_calls = 0
        self.start_time = 0
        self.items_processed = 0
        self.routes_found = 0
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=30, limit_per_host=10),
            timeout=aiohttp.ClientTimeout(total=8)
        )
        self.mongo_service = get_mongodb_service()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.mongo_service:
            self.mongo_service.close()
    
    async def get_profitable_items(self, limit: int = 50) -> List[Dict]:
        """Get most profitable items from database"""
        try:
            collection = self.mongo_service.db["discovered_items"]
            items = list(
                collection.find({"overall_score": {"$gte": 0.2}})  # Lower threshold to get more items
                .sort("overall_score", -1)
                .limit(limit)
            )
            
            # If no items in database, use basic minerals as fallback
            if not items:
                logger.info("No items in database, using basic minerals as fallback")
                items = [
                    {"type_id": 34, "name": "Tritanium", "overall_score": 0.8},
                    {"type_id": 35, "name": "Pyerite", "overall_score": 0.7},
                    {"type_id": 36, "name": "Mexallon", "overall_score": 0.6},
                    {"type_id": 37, "name": "Isogen", "overall_score": 0.5},
                    {"type_id": 38, "name": "Nocxium", "overall_score": 0.4}
                ]
            
            logger.info(f"Selected {len(items)} items for analysis")
            for item in items[:5]:  # Show first 5 items
                logger.info(f"  • {item['name']} (ID: {item['type_id']}, Score: {item.get('overall_score', 0):.2f})")
            
            return items
        except Exception as e:
            logger.error(f"Database error: {e}")
            # Fallback to basic minerals
            return [
                {"type_id": 34, "name": "Tritanium", "overall_score": 0.8},
                {"type_id": 35, "name": "Pyerite", "overall_score": 0.7},
                {"type_id": 36, "name": "Mexallon", "overall_score": 0.6}
            ]
    
    async def fetch_hub_market_orders(self, hub_name: str, type_ids: List[int]) -> Dict[int, List[Dict]]:
        """Fetch market orders for multiple items in a single hub efficiently"""
        region_id = self.HUBS[hub_name]["region_id"]
        orders_by_type = defaultdict(list)
        
        try:
            # Strategy: Fetch all market orders for the region in batches by page
            # This is more efficient than per-item queries
            logger.info(f"Fetching market data for {hub_name}...")
            
            page = 1
            while page <= 10:  # Limit pages for performance
                url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/"
                params = {"datasource": "tranquility", "page": page}
                
                async with self.session.get(url, params=params) as response:
                    self.api_calls += 1
                    
                    if response.status == 404:  # No more pages
                        break
                    elif response.status != 200:
                        logger.warning(f"API error {response.status} for {hub_name}")
                        break
                    
                    orders = await response.json()
                    if not orders:
                        break
                    
                    # Filter and group orders for our target items
                    for order in orders:
                        if order['type_id'] in type_ids:
                            orders_by_type[order['type_id']].append(order)
                    
                    # Check if we have enough data for our items
                    found_items = len(orders_by_type)
                    if found_items >= len(type_ids) * 0.8:  # 80% coverage is good enough
                        break
                    
                    page += 1
            
            logger.info(f"✓ {hub_name}: Found orders for {len(orders_by_type)} items ({self.api_calls} calls)")
            return dict(orders_by_type)
            
        except Exception as e:
            logger.error(f"Error fetching {hub_name}: {e}")
            return {}
    
    async def fetch_all_hub_data(self, type_ids: List[int]) -> Dict[str, Dict[int, List[Dict]]]:
        """Fetch market data for all hubs in parallel"""
        logger.info(f"Fetching market data for {len(self.HUBS)} hubs in parallel...")
        
        tasks = [
            self.fetch_hub_market_orders(hub_name, type_ids)
            for hub_name in self.HUBS.keys()
        ]
        
        results = await asyncio.gather(*tasks)
        
        hub_data = {
            hub_name: result
            for hub_name, result in zip(self.HUBS.keys(), results)
        }
        
        total_items = sum(len(data) for data in hub_data.values())
        logger.info(f"✓ Fetched data for {total_items} item-hub combinations")
        
        return hub_data
    
    def analyze_item_routes(self, type_id: int, item_name: str, 
                           hub_data: Dict[str, Dict[int, List[Dict]]]) -> List[OptimizedRoute]:
        """Analyze all routes for a single item across hubs"""
        routes = []
        
        # Get hub prices for this item
        hub_prices = {}
        for hub_name, orders_data in hub_data.items():
            orders = orders_data.get(type_id, [])
            if not orders:
                continue
            
            # Calculate best buy and sell prices
            sell_orders = [o for o in orders if not o.get('is_buy_order', False)]
            buy_orders = [o for o in orders if o.get('is_buy_order', False)]
            
            if sell_orders and buy_orders:
                best_sell_price = min(o['price'] for o in sell_orders)
                best_buy_price = max(o['price'] for o in buy_orders)
                sell_volume = sum(o['volume_remain'] for o in sell_orders)
                buy_volume = sum(o['volume_remain'] for o in buy_orders)
                
                hub_prices[hub_name] = {
                    'sell_price': best_sell_price,  # Price to buy from
                    'buy_price': best_buy_price,   # Price to sell to
                    'sell_volume': min(sell_volume, 5000),  # Cap volume
                    'buy_volume': min(buy_volume, 5000)
                }
        
        # Find profitable routes between hubs
        for buy_hub, buy_data in hub_prices.items():
            for sell_hub, sell_data in hub_prices.items():
                if buy_hub == sell_hub:
                    continue
                
                # We buy from sell orders, sell to buy orders
                buy_price = buy_data['sell_price']
                sell_price = sell_data['buy_price']
                
                if sell_price <= buy_price:
                    continue  # No profit
                
                # Calculate optimal quantity
                max_buy = buy_data['sell_volume']
                max_sell = sell_data['buy_volume']
                quantity = min(max_buy, max_sell, 1000)  # Conservative limit
                
                if quantity < 10:  # More reasonable minimum quantity
                    continue
                
                # Calculate profits
                gross_profit_per_unit = sell_price - buy_price
                gross_profit_total = gross_profit_per_unit * quantity
                
                # Get travel data
                route_key = (buy_hub, sell_hub)
                reverse_key = (sell_hub, buy_hub)
                
                if route_key in self.TRAVEL_DATA:
                    travel = self.TRAVEL_DATA[route_key]
                elif reverse_key in self.TRAVEL_DATA:
                    travel = self.TRAVEL_DATA[reverse_key]
                else:
                    travel = {"jumps": 15, "minutes": 35, "cost_multiplier": 0.035}
                
                # Calculate costs and net profit
                transport_cost = buy_price * quantity * travel['cost_multiplier']
                net_profit = gross_profit_total - transport_cost
                profit_percent = (net_profit / (buy_price * quantity)) * 100
                
                # Minimum profitability filter (more realistic thresholds)
                if net_profit < 50000 or profit_percent < 3:  # 50k ISK minimum, 3% minimum margin
                    continue
                
                # Calculate time efficiency
                time_minutes = travel['minutes'] + 15  # +15 for docking/undocking
                isk_per_hour = (net_profit / time_minutes) * 60 if time_minutes > 0 else 0
                
                # AI evaluation
                ai_score = self._evaluate_route_ai(
                    profit_percent, quantity, isk_per_hour, net_profit, 
                    travel['jumps'], max_buy, max_sell
                )
                
                # Only include routes the AI approves
                if ai_score < 40:  # More reasonable threshold
                    continue
                
                # AI verdict and risk assessment
                if ai_score > 85:
                    ai_verdict = "EXCELLENT"
                    risk_assessment = "Low Risk"
                elif ai_score > 75:
                    ai_verdict = "VERY GOOD"
                    risk_assessment = "Low-Med Risk"
                elif ai_score > 65:
                    ai_verdict = "GOOD"
                    risk_assessment = "Medium Risk"
                else:
                    ai_verdict = "DECENT"
                    risk_assessment = "Med-High Risk"
                
                routes.append(OptimizedRoute(
                    item_name=item_name,
                    type_id=type_id,
                    buy_hub=buy_hub,
                    sell_hub=sell_hub,
                    buy_price=buy_price,
                    sell_price=sell_price,
                    quantity=quantity,
                    gross_profit=gross_profit_total,
                    transport_cost=transport_cost,
                    net_profit=net_profit,
                    profit_percent=profit_percent,
                    time_minutes=time_minutes,
                    isk_per_hour=isk_per_hour,
                    ai_score=ai_score,
                    ai_verdict=ai_verdict,
                    risk_assessment=risk_assessment
                ))
        
        return routes
    
    def _evaluate_route_ai(self, profit_pct: float, quantity: int, isk_per_hour: float,
                          net_profit: float, jumps: int, available: int, demand: int) -> float:
        """Enhanced AI route evaluation"""
        score = 0
        
        # Profit percentage (0-25 points)
        if profit_pct > 20:
            score += 25
        elif profit_pct > 15:
            score += 20
        elif profit_pct > 10:
            score += 15
        elif profit_pct > 7:
            score += 10
        elif profit_pct > 5:
            score += 5
        
        # ISK per hour vs opportunity cost (0-25 points)
        hourly_target = self.ai_brain.profile.hourly_opportunity_cost
        if isk_per_hour > hourly_target * 3:
            score += 25
        elif isk_per_hour > hourly_target * 2:
            score += 20
        elif isk_per_hour > hourly_target * 1.5:
            score += 15
        elif isk_per_hour > hourly_target:
            score += 10
        elif isk_per_hour > hourly_target * 0.7:
            score += 5
        
        # Net profit absolute (0-20 points)
        if net_profit > 5_000_000:
            score += 20
        elif net_profit > 2_000_000:
            score += 15
        elif net_profit > 1_000_000:
            score += 10
        elif net_profit > 500_000:
            score += 5
        
        # Volume/liquidity (0-15 points)
        min_volume = min(available, demand)
        if min_volume > 500:
            score += 15
        elif min_volume > 200:
            score += 10
        elif min_volume > 100:
            score += 8
        elif min_volume > 50:
            score += 5
        
        # Distance efficiency (0-10 points)
        if jumps < 12:
            score += 10
        elif jumps < 18:
            score += 7
        elif jumps < 25:
            score += 4
        
        # Market balance (0-5 points)
        balance = min(available, demand) / max(available, demand) if max(available, demand) > 0 else 0
        if balance > 0.7:  # Good balance
            score += 5
        elif balance > 0.4:
            score += 3
        
        return min(100, score)
    
    async def find_optimized_routes(self, max_items: int = 30) -> List[OptimizedRoute]:
        """Find optimized routes with efficient processing"""
        self.start_time = time.time()
        logger.info(f"🎯 Starting optimized route analysis for {max_items} items")
        
        # Get profitable items
        items = await self.get_profitable_items(limit=max_items)
        if not items:
            return []
        
        type_ids = [item["type_id"] for item in items]
        item_names = {item["type_id"]: item["name"] for item in items}
        self.items_processed = len(items)
        
        # Fetch all market data in parallel
        hub_data = await self.fetch_all_hub_data(type_ids)
        
        # Analyze routes for all items
        all_routes = []
        logger.info("Analyzing routes for all items...")
        
        for type_id in type_ids:
            item_name = item_names[type_id]
            routes = self.analyze_item_routes(type_id, item_name, hub_data)
            if routes:
                logger.info(f"  ✅ {item_name}: Found {len(routes)} profitable routes")
            all_routes.extend(routes)
        
        # Sort by AI score
        all_routes.sort(key=lambda x: x.ai_score, reverse=True)
        self.routes_found = len(all_routes)
        
        # Performance summary
        total_time = time.time() - self.start_time
        logger.info(f"✅ Analysis complete in {total_time:.1f}s")
        logger.info(f"   • Items analyzed: {self.items_processed}")
        logger.info(f"   • API calls: {self.api_calls}")
        logger.info(f"   • Routes found: {self.routes_found}")
        logger.info(f"   • Performance: {self.items_processed/total_time:.1f} items/sec")
        
        return all_routes[:25]  # Return top 25 routes
    
    def display_results(self, routes: List[OptimizedRoute]):
        """Display optimized results"""
        print("\n" + "="*100)
        print("🎯 FINAL OPTIMIZED PROFITABLE ROUTES")
        print("="*100)
        
        if not routes:
            print("No routes found meeting AI criteria.")
            print("Try lowering AI score threshold or increasing item count.")
            return
        
        total_time = time.time() - self.start_time
        
        # Performance metrics
        print(f"⚡ PERFORMANCE:")
        print(f"   Analysis time: {total_time:.1f}s")
        print(f"   Items analyzed: {self.items_processed}")
        print(f"   API calls made: {self.api_calls}")
        print(f"   Routes found: {self.routes_found}")
        print(f"   Efficiency: {self.routes_found/max(self.api_calls, 1):.1f} routes per API call")
        
        # Top opportunities
        print(f"\n🏆 TOP {min(10, len(routes))} OPPORTUNITIES (AI-Approved):")
        print(f"{'#':<2} {'Item':<18} {'Route':<12} {'Qty':<6} {'Profit':<12} {'%':<7} {'ISK/hr':<10} {'AI':<6} {'Verdict'}")
        print("-"*95)
        
        for i, route in enumerate(routes[:10], 1):
            route_str = f"{route.buy_hub[:3]}→{route.sell_hub[:3]}"
            item_short = route.item_name[:17] if len(route.item_name) > 17 else route.item_name
            
            print(f"{i:<2} {item_short:<18} {route_str:<12} "
                  f"{route.quantity:<6,} {route.net_profit:>11,.0f} "
                  f"{route.profit_percent:>6.1f}% {route.isk_per_hour:>9,.0f} "
                  f"{route.ai_score:>5.0f} {route.ai_verdict}")
        
        # Summary statistics
        if routes:
            total_profit = sum(r.net_profit for r in routes[:5])
            avg_margin = np.mean([r.profit_percent for r in routes[:5]])
            avg_time = np.mean([r.time_minutes for r in routes[:5]])
            
            print(f"\n📊 TOP 5 ROUTES SUMMARY:")
            print(f"   Total potential profit: {total_profit:,.0f} ISK")
            print(f"   Average profit margin: {avg_margin:.1f}%")
            print(f"   Average completion time: {avg_time:.0f} minutes")
            print(f"   Best single opportunity: {routes[0].net_profit:,.0f} ISK")
        
        # Route distribution
        hub_pairs = defaultdict(int)
        for route in routes:
            pair = f"{route.buy_hub}→{route.sell_hub}"
            hub_pairs[pair] += 1
        
        print(f"\n🗺️  BEST TRADING ROUTES:")
        for pair, count in sorted(hub_pairs.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"   {pair}: {count} profitable opportunities")

async def main():
    """Main demonstration"""
    print("🎯 EVE FINAL OPTIMIZED ROUTE FINDER")
    print("="*55)
    print("Efficient • Real-time • AI-Enhanced")
    print("="*55)
    
    # Optimized trader profile
    profile = TraderProfile(
        available_capital=1_500_000_000,  # 1.5B ISK
        risk_tolerance="medium",
        preferred_profit_margin=10.0,
        hourly_opportunity_cost=60_000_000  # 60M ISK/hour
    )
    
    async with FinalOptimizedRouteFinder(profile) as finder:
        print(f"\n📋 Trader Profile:")
        print(f"   Capital: {profile.available_capital:,.0f} ISK")
        print(f"   Risk tolerance: {profile.risk_tolerance}")
        print(f"   Target profit margin: {profile.preferred_profit_margin}%+")
        print(f"   Opportunity cost: {profile.hourly_opportunity_cost:,.0f} ISK/hour")
        
        routes = await finder.find_optimized_routes(max_items=30)
        finder.display_results(routes)

if __name__ == "__main__":
    asyncio.run(main())
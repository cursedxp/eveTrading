"""
Local Market Analyzer - Become the most profitable trader in your system
Focuses on local market dynamics, competition analysis, and system-specific opportunities
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from database_simple import SimpleDatabaseManager
from eve_items_database import EVE_ITEMS, get_item_names
from eve_systems_lookup import EVESystemsLookup
from mongodb_service import get_mongodb_service

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class LocalMarketOpportunity:
    type_id: int
    item_name: str
    current_buy_price: float
    current_sell_price: float
    profit_margin: float
    volume_available: int
    competition_count: int
    market_depth: int
    price_volatility: float
    local_demand: str  # "High", "Medium", "Low"
    local_supply: str  # "High", "Medium", "Low"
    opportunity_type: str  # "Undersupplied", "Oversupplied", "Arbitrage", "Stable"
    score: float
    recommendation: str
    action_plan: str
    buy_location: str  # Source system for buying
    sell_location: str  # Target system for selling
    transport_cost: float = 0.0  # Transport cost for cross-system trades
    net_profit_margin: float = 0.0  # Net profit after transport costs
    net_profit_percent: float = 0.0  # Net profit percentage

@dataclass
class LocalMarketAnalysis:
    system_name: str
    total_opportunities: int
    avg_profit_margin: float
    market_health: str
    competition_level: str
    best_opportunities: List[LocalMarketOpportunity]
    market_gaps: List[str]
    strategic_recommendations: List[str]

class LocalMarketAnalyzer:
    def __init__(self, target_system: str = ""):
        self.target_system = target_system
        self.session = None
        self.db = SimpleDatabaseManager()
        self.systems_lookup = None
        self.system_info = None
        self.region_id = None
        
        # Cache for system information
        self._system_cache = {}
        self._region_cache = {}
        self._stations_cache = {}
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        self.systems_lookup = EVESystemsLookup()
        await self.systems_lookup.__aenter__()
        
        # Load system information dynamically
        if self.target_system:
            await self._load_system_info()
        
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        if self.systems_lookup:
            await self.systems_lookup.__aexit__(exc_type, exc_val, exc_tb)
    
    async def _load_system_info(self):
        """Load system information dynamically from ESI"""
        if self.target_system in self._system_cache:
            self.system_info = self._system_cache[self.target_system]
            self.region_id = self.system_info.get('region_id')
            return
        
        logger.info(f"Looking up system information for: {self.target_system}")
        self.system_info = await self.systems_lookup.search_system(self.target_system)
        
        if self.system_info:
            self.region_id = self.system_info.get('region_id')
            self._system_cache[self.target_system] = self.system_info
            logger.info(f"System found: {self.target_system} in region {self.system_info.get('region_name')} (ID: {self.region_id})")
        else:
            logger.warning(f"System {self.target_system} not found. Using default region (The Forge)")
            self.region_id = 10000002  # Default to The Forge
    
    async def get_stations_in_system(self, system_id: int) -> List[int]:
        """Get all station IDs in a system"""
        if system_id in self._stations_cache:
            return self._stations_cache[system_id]
        
        try:
            # Get system info including stations
            system_url = f"https://esi.evetech.net/latest/universe/systems/{system_id}/"
            
            async with self.session.get(system_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to get system info for {system_id}: {response.status}")
                    return []
                
                system_data = await response.json()
                station_ids = system_data.get('stations', [])
                
                # Cache the result
                self._stations_cache[system_id] = station_ids
                logger.info(f"Found {len(station_ids)} stations in {self.target_system}: {station_ids}")
                
                return station_ids
                
        except Exception as e:
            logger.error(f"Error getting stations for system {system_id}: {e}")
            return []
    
    def get_system_profile(self) -> Dict:
        """Get market profile for the target system dynamically"""
        if self.system_info and self.systems_lookup:
            # Get dynamic profile based on system characteristics
            profile = self.systems_lookup.estimate_market_profile(
                self.target_system,
                self.system_info.get('security_status', 0.5)
            )
            
            # Add some best items based on profile
            if "Everything" in profile.get("specialization", ""):
                profile["best_items"] = ["Tritanium", "Pyerite", "Mexallon", "Isogen"]
            elif "Minerals" in profile.get("specialization", ""):
                profile["best_items"] = ["Tritanium", "Pyerite", "Mexallon"]
            elif "PvP" in profile.get("specialization", ""):
                profile["best_items"] = ["Antimatter Charge M", "Warp Disruptor II", "Stasis Webifier II"]
            else:
                profile["best_items"] = ["Tritanium", "Pyerite"]
            
            return profile
        
        # Fallback for unknown systems
        return {
            "competition": "Unknown",
            "volume": "Unknown",
            "profit_margins": "Unknown", 
            "specialization": "General Trading",
            "best_items": ["Tritanium", "Pyerite"]
        }
    
    async def run_dynamic_discovery(self, max_items: int = 50) -> List[Dict]:
        """Run dynamic item discovery using the DynamicItemDiscovery system"""
        try:
            from dynamic_item_discovery import DynamicItemDiscovery
            
            logger.info("Running dynamic item discovery from ESI API...")
            # Use dynamic region ID or default to The Forge
            region_id = self.region_id if self.region_id else 10000002
            
            async with DynamicItemDiscovery(region_id) as discoverer:
                # Discover profitable items
                items = await discoverer.discover_profitable_items(min_score=0.3, max_items=max_items)
                
                if items:
                    # Convert to the format expected by analyze_local_market
                    popular_items = []
                    for item in items:
                        popular_items.append({
                            'type_id': item.type_id,
                            'name': item.name
                        })
                    
                    # Update database with discovered items
                    await discoverer.update_database_with_discovered_items(items)
                    logger.info(f"✅ Dynamic discovery found {len(popular_items)} profitable items")
                    return popular_items
                else:
                    logger.warning("Dynamic discovery found no profitable items")
                    return []
                    
        except Exception as e:
            logger.error(f"Error in dynamic discovery: {e}")
            return []
    
    def find_most_profitable_system(self, item_name: str, current_system: str) -> str:
        """Find the most profitable system for selling an item"""
        # Get dynamic list of trading systems
        # For now, use some major hubs, but this could be expanded
        major_hubs = ["Jita", "Amarr", "Dodixie", "Rens", "Hek", "Perimeter", "Ashab"]
        
        # Remove current system from options
        available_systems = [hub for hub in major_hubs if hub != current_system]
        
        if not available_systems:
            return current_system  # If no other systems available, return current
        
        # Simple logic to find best system based on item type and system characteristics
        if item_name in ["Tritanium", "Pyerite", "Mexallon", "Isogen"]:  # Minerals
            # For minerals, prefer Jita or Amarr if available
            if "Jita" in available_systems:
                return "Jita"
            elif "Amarr" in available_systems:
                return "Amarr"
            else:
                return available_systems[0]
        
        elif item_name in ["Warrior II", "Hammerhead II", "Ogre II"]:  # Drones
            # Drones do well in Hek
            if "Hek" in available_systems:
                return "Hek"
            else:
                return available_systems[0]
        
        elif item_name in ["Antimatter Charge S", "Antimatter Charge M", "Antimatter Charge L"]:  # Ammunition
            # Ammunition does well in Rens
            if "Rens" in available_systems:
                return "Rens"
            else:
                return available_systems[0]
        
        elif item_name in ["Mechanical Parts", "Construction Blocks", "Hull Sections"]:  # Components
            # Components do well in Dodixie
            if "Dodixie" in available_systems:
                return "Dodixie"
            else:
                return available_systems[0]
        
        else:  # Default: return random major hub
            import random
            return random.choice(available_systems)
    
    async def get_region_market_data(self, type_id: int) -> List[Dict]:
        """Get market data for analysis using the correct region and system"""
        try:
            # Use dynamic region ID or default to The Forge
            region_id = self.region_id if self.region_id else 10000002
            
            sell_url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type=sell&type_id={type_id}"
            buy_url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type=buy&type_id={type_id}"
            
            async with self.session.get(sell_url) as sell_response, self.session.get(buy_url) as buy_response:
                sell_orders = await sell_response.json() if sell_response.status == 200 else []
                buy_orders = await buy_response.json() if buy_response.status == 200 else []
                
                # Filter orders to only include those from the target system
                system_id = self.system_info.get('system_id') if self.system_info else None
                
                if system_id:
                    # Get all station IDs in the target system first
                    stations_in_system = await self.get_stations_in_system(system_id)
                    
                    if stations_in_system:
                        # Filter orders to only those in stations within the target system
                        sell_orders = [order for order in sell_orders if order.get('location_id') in stations_in_system]
                        buy_orders = [order for order in buy_orders if order.get('location_id') in stations_in_system]
                        logger.info(f"Filtered to {len(sell_orders)} sell orders and {len(buy_orders)} buy orders in {self.target_system} stations")
                    else:
                        logger.warning(f"No stations found for {self.target_system}, using all regional orders")
                else:
                    logger.warning(f"No system_id found for {self.target_system}, using all regional orders")
                
                for order in sell_orders:
                    order['order_type'] = 'sell'
                for order in buy_orders:
                    order['order_type'] = 'buy'
                
                return sell_orders + buy_orders
        except Exception as e:
            logger.error(f"Error fetching market data for {type_id}: {e}")
            return []
    
    def analyze_local_opportunity(self, orders: List[Dict], item: Dict, system_profile: Dict) -> Optional[LocalMarketOpportunity]:
        """Analyze local market opportunity for an item"""
        if not orders:
            return None
        
        # Separate buy and sell orders
        sell_orders = [o for o in orders if o['order_type'] == 'sell']
        buy_orders = [o for o in orders if o['order_type'] == 'buy']
        
        if not sell_orders or not buy_orders:
            return None
        
        # Calculate market metrics
        # Buy price: lowest sell order (what you pay to buy from someone)
        # Sell price: highest buy order (what you get when selling to someone)
        current_buy_price = min(o['price'] for o in sell_orders)  # Lowest sell order (best price to buy)
        current_sell_price = max(o['price'] for o in buy_orders)  # Highest buy order (best price to sell)
        
        # Profit margin: (sell_price - buy_price) / buy_price
        # This represents the percentage profit you make when buying at lowest sell price and selling at highest buy price
        profit_margin = (current_sell_price - current_buy_price) / current_buy_price if current_buy_price > 0 else 0
        
        # Debug logging for profit margins (only log truly positive margins)
        if profit_margin > 0.001:  # Log any margin > 0.1%
            logger.info(f"PROFITABLE OPPORTUNITY: {item['name']} - Buy: {current_buy_price:.2f}, Sell: {current_sell_price:.2f}, Margin: {profit_margin:.4f} ({profit_margin*100:.2f}%)")
        
        # VALIDATION: Sanity check for unrealistic profit margins
        # In EVE Online, profit margins above 50% are extremely rare and usually indicate data issues
        if profit_margin > 0.5:  # 50% profit margin
            logger.warning(f"Unrealistic profit margin detected: {profit_margin:.2%} for {item.get('name', 'Unknown')}")
            logger.warning(f"Buy price: {current_buy_price}, Sell price: {current_sell_price}")
            logger.info(f"Raw profit margin: {profit_margin:.4f} ({profit_margin*100:.2f}%)")
            # Cap the profit margin at 50% to prevent unrealistic values
            profit_margin = min(profit_margin, 0.5)
        
        # Additional validation: Check for negative profit margins (shouldn't happen in normal cases)
        if profit_margin < 0:
            logger.warning(f"Negative profit margin detected: {profit_margin:.2%} for {item.get('name', 'Unknown')}")
            logger.info(f"Raw profit margin: {profit_margin:.4f} ({profit_margin*100:.2f}%)")
            profit_margin = 0
        
        # Calculate volume and competition
        volume_available = sum(o.get('volume_remain', 0) for o in orders)
        competition_count = len(set(o.get('character_id', 0) for o in orders))
        market_depth = len(orders)
        
        # Calculate price volatility (simplified)
        prices = [o['price'] for o in orders]
        price_volatility = np.std(prices) / np.mean(prices) if prices else 0
        
        # Determine local demand and supply
        buy_volume = sum(o.get('volume_remain', 0) for o in buy_orders)
        sell_volume = sum(o.get('volume_remain', 0) for o in sell_orders)
        
        if buy_volume > sell_volume * 2:
            local_demand = "High"
        elif buy_volume > sell_volume:
            local_demand = "Medium"
        else:
            local_demand = "Low"
            
        if sell_volume > buy_volume * 2:
            local_supply = "High"
        elif sell_volume > buy_volume:
            local_supply = "Medium"
        else:
            local_supply = "Low"
        
        # Determine opportunity type
        if local_demand == "High" and local_supply == "Low":
            opportunity_type = "Undersupplied"
        elif local_demand == "Low" and local_supply == "High":
            opportunity_type = "Oversupplied"
        elif profit_margin > 0.1:  # 10% margin
            opportunity_type = "Arbitrage"
        else:
            opportunity_type = "Stable"
        
        # Calculate score based on system profile
        base_score = profit_margin * 0.4
        competition_score = (1.0 - competition_count / 100) * 0.3  # Lower competition = higher score
        volume_score = min(1.0, volume_available / 10000) * 0.2
        volatility_score = min(1.0, price_volatility * 10) * 0.1
        
        # Adjust for system characteristics
        if system_profile["competition"] == "Very High":
            competition_score *= 0.5  # Reduce score in very competitive markets
        elif system_profile["competition"] == "Low":
            competition_score *= 1.5  # Boost score in less competitive markets
        
        score = base_score + competition_score + volume_score + volatility_score
        
        # Determine recommendation
        if score > 0.7:
            recommendation = "STRONG BUY"
        elif score > 0.5:
            recommendation = "BUY"
        elif score > 0.3:
            recommendation = "HOLD"
        else:
            recommendation = "SELL"
        
        # Create action plan for local trading within the system
        if opportunity_type == "Undersupplied":
            action_plan = f"Buy {item['name']} at {current_buy_price:.0f} ISK and sell locally in {self.target_system}"
        elif opportunity_type == "Oversupplied":
            action_plan = f"Monitor {item['name']} for better prices in {self.target_system}"
        elif opportunity_type == "Arbitrage":
            action_plan = f"Buy low at {current_buy_price:.0f} ISK, sell high at {current_sell_price:.0f} ISK in {self.target_system}"
        else:
            action_plan = f"Monitor {item['name']} for price movements in {self.target_system}"
        
        # For local market analysis, always keep buy and sell in the same system
        # This ensures we only show local arbitrage opportunities
        buy_location = self.target_system
        sell_location = self.target_system
        
        # For local market analysis, transport cost is always 0
        transport_cost = 0.0
        
        # Calculate net profit
        gross_profit = (current_sell_price - current_buy_price) * 1000  # Assume 1000 units for calculation
        net_profit = gross_profit - transport_cost
        net_profit_margin = net_profit / (current_buy_price * 1000) if current_buy_price > 0 else 0
        net_profit_percent = (net_profit_margin * 100) if net_profit_margin > 0 else 0
        
        return LocalMarketOpportunity(
            type_id=item['type_id'],
            item_name=item['name'],
            current_buy_price=current_buy_price,
            current_sell_price=current_sell_price,
            profit_margin=profit_margin,
            volume_available=volume_available,
            competition_count=competition_count,
            market_depth=market_depth,
            price_volatility=price_volatility,
            local_demand=local_demand,
            local_supply=local_supply,
            opportunity_type=opportunity_type,
            score=score,
            recommendation=recommendation,
            action_plan=action_plan,
            buy_location=buy_location,
            sell_location=sell_location,
            transport_cost=transport_cost,
            net_profit_margin=net_profit_margin,
            net_profit_percent=net_profit_percent
        )
    
    async def analyze_local_market(self, max_items: int = 150) -> LocalMarketAnalysis:
        """Analyze local market opportunities"""
        # Use dynamic region ID
        region_id = self.region_id if self.region_id else 10000002
        logger.info(f"Analyzing market opportunities in {self.target_system} (Region ID: {region_id})...")
        
        system_profile = self.get_system_profile()
        logger.info(f"System Profile: {system_profile['specialization']} market, {system_profile['competition']} competition")
        
        # Focus on system-specialized items
        specialized_items = system_profile.get('best_items', [])
        
        # Try to get discovered items from database first
        discovered_items_df = self.db.get_top_discovered_items(limit=150, min_score=0.3)
        
        if not discovered_items_df.empty:
            # Use discovered items from database
            popular_items = []
            for _, row in discovered_items_df.iterrows():
                popular_items.append({
                    'type_id': int(row['type_id']),
                    'name': row['name']
                })
            logger.info(f"Using {len(popular_items)} discovered items from database")
        else:
            # If no discovered items, run dynamic discovery to populate the database
            logger.info("No discovered items found in database. Running dynamic discovery...")
            popular_items = await self.run_dynamic_discovery(max_items)
            
            if not popular_items:
                # Only use minimal fallback if dynamic discovery completely fails
                logger.warning("Dynamic discovery failed. Using test items for arbitrage potential.")
                popular_items = [
                    {'type_id': 34, 'name': 'Tritanium'},
                    {'type_id': 35, 'name': 'Pyerite'},
                    {'type_id': 36, 'name': 'Mexallon'},
                    {'type_id': 37, 'name': 'Isogen'},
                    {'type_id': 2203, 'name': 'Warrior II'},
                    {'type_id': 2488, 'name': 'Antimatter Charge M'},
                    {'type_id': 3532, 'name': 'Large Shield Extender II'},
                    {'type_id': 519, 'name': 'Veldspar'},
                    {'type_id': 11399, 'name': 'Scourge Heavy Missile'},
                    {'type_id': 12058, 'name': 'Core Probe Launcher I'}
                ]
        
        # Prioritize specialized items
        prioritized_items = []
        for item in popular_items:
            if item['name'] in specialized_items:
                prioritized_items.insert(0, item)  # Add specialized items first
            else:
                prioritized_items.append(item)
        
        opportunities = []
        analyzed_count = 0
        
        for item in prioritized_items[:max_items]:
            try:
                logger.info(f"Analyzing {item['name']} in {self.target_system}...")
                
                # Get market data
                orders = await self.get_region_market_data(item['type_id'])
                
                if orders:
                    opportunity = self.analyze_local_opportunity(orders, item, system_profile)
                    # TEMP: Include all opportunities, even unprofitable ones, for debugging
                    if opportunity:  # Removed net_profit_percent > 0 filter
                        opportunities.append(opportunity)
                        analyzed_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error analyzing {item['name']}: {e}")
                continue
        
        # Temporarily disabled same location filter to show more opportunities
        # opportunities = [opp for opp in opportunities if opp.buy_location != opp.sell_location]
        
        # Sort by net profit percentage first, then by score
        opportunities.sort(key=lambda x: (x.net_profit_percent, x.score), reverse=True)
        
        # Calculate market health based on net profit
        avg_net_profit_percent = np.mean([o.net_profit_percent for o in opportunities]) if opportunities else 0
        total_opportunities = len(opportunities)
        
        if avg_net_profit_percent > 15:
            market_health = "Excellent"
        elif avg_net_profit_percent > 10:
            market_health = "Good"
        elif avg_net_profit_percent > 5:
            market_health = "Fair"
        else:
            market_health = "Poor"
        
        # Identify market gaps
        market_gaps = []
        if not any(o.opportunity_type == "Undersupplied" for o in opportunities):
            market_gaps.append("No undersupplied items found")
        if not any(o.opportunity_type == "Arbitrage" for o in opportunities):
            market_gaps.append("Limited arbitrage opportunities")
        if avg_net_profit_percent < 5.0:  # Changed from avg_profit_margin to avg_net_profit_percent and adjusted threshold
            market_gaps.append("Low profit margins overall")
        
        # Generate strategic recommendations
        strategic_recommendations = []
        
        if system_profile["competition"] == "Very High":
            strategic_recommendations.append("Focus on high-volume, low-competition items")
            strategic_recommendations.append("Consider off-peak trading hours")
        elif system_profile["competition"] == "Low":
            strategic_recommendations.append("Capitalize on low competition with higher margins")
            strategic_recommendations.append("Expand into multiple item categories")
        
        if any(o.opportunity_type == "Undersupplied" for o in opportunities):
            strategic_recommendations.append("Import undersupplied items from other systems")
        
        if any(o.opportunity_type == "Arbitrage" for o in opportunities):
            strategic_recommendations.append("Focus on arbitrage opportunities within the system")
        
        strategic_recommendations.append(f"Specialize in {system_profile['specialization']} items")
        
        logger.info(f"Analysis complete: {total_opportunities} opportunities found in {self.target_system}")
        
        return LocalMarketAnalysis(
            system_name=self.target_system,
            total_opportunities=total_opportunities,
            avg_profit_margin=avg_net_profit_percent / 100,  # Convert percentage to decimal for compatibility
            market_health=market_health,
            competition_level=system_profile["competition"],
            best_opportunities=opportunities[:100],  # Increased to 100 to show more profitable opportunities
            market_gaps=market_gaps,
            strategic_recommendations=strategic_recommendations
        )
    
    def display_local_analysis(self, analysis: LocalMarketAnalysis):
        """Display market analysis results"""
        print(f"\n{'='*100}")
        print(f"MARKET ANALYSIS: {analysis.system_name}")
        print(f"{'='*100}")
        print(f"Market Health: {analysis.market_health}")
        print(f"Competition Level: {analysis.competition_level}")
        print(f"Total Opportunities: {analysis.total_opportunities}")
        print(f"Average Profit Margin: {analysis.avg_profit_margin:.2%}")
        print(f"{'='*100}")
        
        if analysis.best_opportunities:
            print(f"{'Item Name':<25} {'Buy':<10} {'Sell':<10} {'Profit %':<10} {'Demand':<8} {'Supply':<8} {'Type':<12} {'Score':<8} {'Rec':<10}")
            print("-"*100)
            
            for opportunity in analysis.best_opportunities:
                print(f"{opportunity.item_name:<25} {opportunity.current_buy_price:<9.2f} "
                      f"{opportunity.current_sell_price:<9.2f} {opportunity.profit_margin*100:<9.1f}% "
                      f"{opportunity.local_demand:<8} {opportunity.local_supply:<8} "
                      f"{opportunity.opportunity_type:<12} {opportunity.score:<7.2f} {opportunity.recommendation:<10}")
            
            print("-"*100)
            
            # Show action plans
            print(f"\n📋 ACTION PLANS:")
            for opportunity in analysis.best_opportunities[:5]:
                print(f"  • {opportunity.item_name}: {opportunity.action_plan}")
            
            # Show market gaps
            if analysis.market_gaps:
                print(f"\n⚠️  MARKET GAPS:")
                for gap in analysis.market_gaps:
                    print(f"  • {gap}")
            
            # Show strategic recommendations
            print(f"\n🎯 STRATEGIC RECOMMENDATIONS:")
            for rec in analysis.strategic_recommendations:
                print(f"  • {rec}")
        else:
            print("No profitable opportunities found in this system.")
    
    def export_local_analysis(self, analysis: LocalMarketAnalysis, filename: str = None, use_mongodb: bool = True):
        """Export market analysis to MongoDB and optionally to JSON"""
        data = {
            'system_name': analysis.system_name,
            'analysis_timestamp': datetime.now(),
            'total_opportunities': analysis.total_opportunities,
            'avg_profit_margin': analysis.avg_profit_margin,
            'market_health': analysis.market_health,
            'competition_level': analysis.competition_level,
            'market_gaps': analysis.market_gaps,
            'strategic_recommendations': analysis.strategic_recommendations,
            'opportunities': [
                {
                    'type_id': o.type_id,
                    'item_name': o.item_name,
                    'current_buy_price': o.current_buy_price,
                    'current_sell_price': o.current_sell_price,
                    'profit_margin': o.profit_margin,
                    'volume_available': o.volume_available,
                    'competition_count': o.competition_count,
                    'market_depth': o.market_depth,
                    'price_volatility': o.price_volatility,
                    'local_demand': o.local_demand,
                    'local_supply': o.local_supply,
                    'opportunity_type': o.opportunity_type,
                    'score': o.score,
                    'recommendation': o.recommendation,
                    'action_plan': o.action_plan,
                    'buy_location': o.buy_location,
                    'sell_location': o.sell_location,
                    'transport_cost': o.transport_cost,
                    'net_profit_margin': o.net_profit_margin
                }
                for o in analysis.best_opportunities
            ]
        }
        
        # Store in MongoDB
        if use_mongodb:
            try:
                mongo_service = get_mongodb_service()
                analysis_id = mongo_service.store_market_analysis(data)
                logger.info(f"Market analysis stored in MongoDB with ID: {analysis_id}")
                
                # Also store trading signals
                signals = [
                    {
                        'timestamp': datetime.now(),
                        'type_id': o.type_id,
                        'item_name': o.item_name,
                        'action': 'STRONG_BUY' if o.recommendation == 'STRONG BUY' else 'BUY',
                        'confidence': o.score,
                        'price': o.current_sell_price,
                        'volume': o.volume_available,
                        'profit_margin': o.profit_margin * 100,
                        'local_demand': o.local_demand,
                        'local_supply': o.local_supply,
                        'opportunity_type': o.opportunity_type,
                        'recommendation': o.recommendation,
                        'action_plan': o.action_plan
                    }
                    for o in analysis.best_opportunities
                ]
                
                signals_count = mongo_service.store_trading_signals(signals, analysis.system_name)
                logger.info(f"Stored {signals_count} trading signals in MongoDB")
                
                mongo_service.close()
                
                # MongoDB storage successful - no JSON fallback needed
                logger.info(f"Market analysis stored in MongoDB with ID: {analysis_id}")
                return
                
            except Exception as e:
                logger.error(f"Error storing in MongoDB: {e}")
                # No fallback to JSON - if MongoDB fails, just log the error
                raise e

async def main():
    """Main function to run local market analysis"""
    print("🎯 EVE Local Market Analyzer")
    print("="*50)
    
    # Available systems
    systems = ["Jita", "Amarr", "Dodixie", "Rens", "Hek"]
    
    print("Available systems:")
    for i, system in enumerate(systems, 1):
        print(f"  {i}. {system}")
    
    # Default to Jita for testing
    target_system = "Jita"
    
    async with LocalMarketAnalyzer(target_system) as analyzer:
        analysis = await analyzer.analyze_local_market(max_items=25)
        analyzer.display_local_analysis(analysis)
        analyzer.export_local_analysis(analysis)

if __name__ == "__main__":
    asyncio.run(main()) 
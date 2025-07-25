"""
System-Based Trading Analyzer - Focuses on specific EVE systems for maximum profitability
Analyzes market opportunities within a specific system to become the most profitable trader
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class SystemMarketOpportunity:
    system_id: int
    system_name: str
    type_id: int
    item_name: str
    current_price: float
    avg_price_system: float
    avg_price_region: float
    price_difference: float
    profit_margin: float
    volume_24h: int
    competition_level: str  # "Low", "Medium", "High"
    market_depth: int
    arbitrage_opportunity: bool
    score: float
    recommendation: str

@dataclass
class SystemAnalysis:
    system_id: int
    system_name: str
    total_opportunities: int
    avg_profit_margin: float
    best_opportunities: List[SystemMarketOpportunity]
    market_activity: str
    competition_level: str
    recommended_items: List[int]

class SystemTradingAnalyzer:
    def __init__(self, target_system_id: int = 60003760):  # Jita 4-4
        self.target_system_id = target_system_id
        self.session = None
        self.db = SimpleDatabaseManager()
        self.system_name = self.get_system_name(target_system_id)
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_system_name(self, system_id: int) -> str:
        """Get system name from ID"""
        system_names = {
            60003760: "Jita",
            60008494: "Amarr",
            60011866: "Dodixie", 
            60004588: "Rens",
            60005686: "Hek",
            60009106: "Oursulaert",
            60012721: "Niarja",
            60014995: "Perimeter",
            60015068: "New Caldari",
            60015169: "Old Man Star"
        }
        return system_names.get(system_id, f"System {system_id}")
    
    async def get_system_market_orders(self, type_id: int) -> List[Dict]:
        """Get market orders for a specific item in the target system"""
        try:
            # Get orders from the specific system
            sell_url = f"https://esi.evetech.net/latest/markets/{self.target_system_id}/orders/?datasource=tranquility&order_type=sell&type_id={type_id}"
            buy_url = f"https://esi.evetech.net/latest/markets/{self.target_system_id}/orders/?datasource=tranquility&order_type=buy&type_id={type_id}"
            
            async with self.session.get(sell_url) as sell_response, self.session.get(buy_url) as buy_response:
                sell_orders = await sell_response.json() if sell_response.status == 200 else []
                buy_orders = await buy_response.json() if buy_response.status == 200 else []
                
                # Add order type and system info
                for order in sell_orders:
                    order['order_type'] = 'sell'
                    order['system_id'] = self.target_system_id
                for order in buy_orders:
                    order['order_type'] = 'buy'
                    order['system_id'] = self.target_system_id
                
                return sell_orders + buy_orders
        except Exception as e:
            logger.error(f"Error fetching system market orders for {type_id}: {e}")
            return []
    
    async def get_region_market_orders(self, type_id: int, region_id: int = 10000002) -> List[Dict]:
        """Get market orders for a specific item in the region for comparison"""
        try:
            sell_url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type=sell&type_id={type_id}"
            buy_url = f"https://esi.evetech.net/latest/markets/{region_id}/orders/?datasource=tranquility&order_type=buy&type_id={type_id}"
            
            async with self.session.get(sell_url) as sell_response, self.session.get(buy_url) as buy_response:
                sell_orders = await sell_response.json() if sell_response.status == 200 else []
                buy_orders = await buy_response.json() if buy_response.status == 200 else []
                
                for order in sell_orders:
                    order['order_type'] = 'sell'
                for order in buy_orders:
                    order['order_type'] = 'buy'
                
                return sell_orders + buy_orders
        except Exception as e:
            logger.error(f"Error fetching region market orders for {type_id}: {e}")
            return []
    
    def calculate_system_opportunity(self, system_orders: List[Dict], region_orders: List[Dict], item: Dict) -> Optional[SystemMarketOpportunity]:
        """Calculate trading opportunity for a specific item in the system"""
        if not system_orders or not region_orders:
            return None
        
        # Separate buy and sell orders
        system_sell_orders = [o for o in system_orders if o['order_type'] == 'sell']
        system_buy_orders = [o for o in system_orders if o['order_type'] == 'buy']
        region_sell_orders = [o for o in region_orders if o['order_type'] == 'sell']
        region_buy_orders = [o for o in region_orders if o['order_type'] == 'buy']
        
        if not system_sell_orders or not system_buy_orders:
            return None
        
        # Calculate system prices
        system_sell_price = min(o['price'] for o in system_sell_orders)
        system_buy_price = max(o['price'] for o in system_buy_orders)
        system_avg_price = (system_sell_price + system_buy_price) / 2
        
        # Calculate region prices
        region_sell_price = min(o['price'] for o in region_sell_orders) if region_sell_orders else system_sell_price
        region_buy_price = max(o['price'] for o in region_buy_orders) if region_buy_orders else system_buy_price
        region_avg_price = (region_sell_price + region_buy_price) / 2
        
        # Calculate metrics
        price_difference = system_avg_price - region_avg_price
        profit_margin = (system_sell_price - system_buy_price) / system_buy_price if system_buy_price > 0 else 0
        volume_24h = sum(o.get('volume_remain', 0) for o in system_orders)
        market_depth = len(system_orders)
        
        # Determine competition level
        if market_depth < 10:
            competition_level = "Low"
        elif market_depth < 50:
            competition_level = "Medium"
        else:
            competition_level = "High"
        
        # Check for arbitrage opportunity
        arbitrage_opportunity = system_buy_price > region_sell_price if region_sell_orders else False
        
        # Calculate overall score
        score = (
            profit_margin * 0.4 +
            (1.0 - market_depth / 100) * 0.3 +  # Lower depth = higher score
            min(1.0, volume_24h / 10000) * 0.2 +  # Volume score
            (0.5 if arbitrage_opportunity else 0.0) * 0.1  # Arbitrage bonus
        )
        
        # Determine recommendation
        if score > 0.7:
            recommendation = "STRONG BUY"
        elif score > 0.5:
            recommendation = "BUY"
        elif score > 0.3:
            recommendation = "HOLD"
        else:
            recommendation = "SELL"
        
        return SystemMarketOpportunity(
            system_id=self.target_system_id,
            system_name=self.system_name,
            type_id=item['type_id'],
            item_name=item['name'],
            current_price=system_avg_price,
            avg_price_system=system_avg_price,
            avg_price_region=region_avg_price,
            price_difference=price_difference,
            profit_margin=profit_margin,
            volume_24h=volume_24h,
            competition_level=competition_level,
            market_depth=market_depth,
            arbitrage_opportunity=arbitrage_opportunity,
            score=score,
            recommendation=recommendation
        )
    
    async def analyze_system_opportunities(self, max_items: int = 50) -> SystemAnalysis:
        """Analyze trading opportunities in the target system"""
        logger.info(f"Analyzing trading opportunities in {self.system_name} (ID: {self.target_system_id})...")
        
        # Get popular trading items
        popular_items = [
            {'type_id': 34, 'name': 'Tritanium'},
            {'type_id': 35, 'name': 'Pyerite'},
            {'type_id': 36, 'name': 'Mexallon'},
            {'type_id': 37, 'name': 'Isogen'},
            {'type_id': 38, 'name': 'Nocxium'},
            {'type_id': 39, 'name': 'Zydrine'},
            {'type_id': 40, 'name': 'Megacyte'},
            {'type_id': 16262, 'name': 'Strontium Clathrates'},
            {'type_id': 16263, 'name': 'Heavy Water'},
            {'type_id': 16264, 'name': 'Liquid Ozone'},
            {'type_id': 16265, 'name': 'Helium Isotopes'},
            {'type_id': 44, 'name': 'Enriched Uranium'},
            {'type_id': 45, 'name': 'Toxic Metals'},
            {'type_id': 46, 'name': 'Reactive Metals'},
            {'type_id': 11529, 'name': 'Mechanical Parts'},
            {'type_id': 11530, 'name': 'Construction Blocks'},
            {'type_id': 11531, 'name': 'Hull Sections'},
            {'type_id': 1, 'name': 'Antimatter Charge S'},
            {'type_id': 2, 'name': 'Antimatter Charge M'},
            {'type_id': 3, 'name': 'Antimatter Charge L'},
            {'type_id': 2203, 'name': 'Warrior II'},
            {'type_id': 2205, 'name': 'Hammerhead II'},
            {'type_id': 2207, 'name': 'Ogre II'},
            {'type_id': 2048, 'name': 'Adaptive Invulnerability Field I'},
            {'type_id': 2049, 'name': 'Adaptive Invulnerability Field II'},
            {'type_id': 2050, 'name': 'Adaptive Invulnerability Field II'},
            {'type_id': 670, 'name': 'Merlin'},
            {'type_id': 671, 'name': 'Punisher'},
            {'type_id': 672, 'name': 'Rifter'}
        ]
        
        opportunities = []
        analyzed_count = 0
        
        for item in popular_items[:max_items]:
            try:
                logger.info(f"Analyzing {item['name']} in {self.system_name}...")
                
                # Get system and region market data
                system_orders = await self.get_system_market_orders(item['type_id'])
                region_orders = await self.get_region_market_orders(item['type_id'])
                
                if system_orders:
                    opportunity = self.calculate_system_opportunity(system_orders, region_orders, item)
                    if opportunity and opportunity.score > 0.3:  # Only include decent opportunities
                        opportunities.append(opportunity)
                        analyzed_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error analyzing {item['name']}: {e}")
                continue
        
        # Sort by score
        opportunities.sort(key=lambda x: x.score, reverse=True)
        
        # Calculate system metrics
        avg_profit_margin = np.mean([o.profit_margin for o in opportunities]) if opportunities else 0
        total_opportunities = len(opportunities)
        
        # Determine market activity level
        if total_opportunities > 20:
            market_activity = "High"
        elif total_opportunities > 10:
            market_activity = "Medium"
        else:
            market_activity = "Low"
        
        # Determine competition level
        avg_competition = np.mean([1 if o.competition_level == "Low" else 2 if o.competition_level == "Medium" else 3 for o in opportunities]) if opportunities else 2
        if avg_competition < 1.5:
            competition_level = "Low"
        elif avg_competition < 2.5:
            competition_level = "Medium"
        else:
            competition_level = "High"
        
        # Get recommended items
        recommended_items = [o.type_id for o in opportunities[:10]]
        
        logger.info(f"Analysis complete: {total_opportunities} opportunities found in {self.system_name}")
        
        return SystemAnalysis(
            system_id=self.target_system_id,
            system_name=self.system_name,
            total_opportunities=total_opportunities,
            avg_profit_margin=avg_profit_margin,
            best_opportunities=opportunities[:10],
            market_activity=market_activity,
            competition_level=competition_level,
            recommended_items=recommended_items
        )
    
    def display_system_analysis(self, analysis: SystemAnalysis):
        """Display system analysis results"""
        print(f"\n{'='*100}")
        print(f"SYSTEM TRADING ANALYSIS: {analysis.system_name}")
        print(f"{'='*100}")
        print(f"System ID: {analysis.system_id}")
        print(f"Market Activity: {analysis.market_activity}")
        print(f"Competition Level: {analysis.competition_level}")
        print(f"Total Opportunities: {analysis.total_opportunities}")
        print(f"Average Profit Margin: {analysis.avg_profit_margin:.2%}")
        print(f"{'='*100}")
        
        if analysis.best_opportunities:
            print(f"{'Item Name':<25} {'Price':<12} {'Profit %':<10} {'Volume':<10} {'Competition':<12} {'Score':<8} {'Rec':<10}")
            print("-"*100)
            
            for opportunity in analysis.best_opportunities:
                print(f"{opportunity.item_name:<25} {opportunity.current_price:<11.2f} "
                      f"{opportunity.profit_margin*100:<9.1f}% {opportunity.volume_24h:<10} "
                      f"{opportunity.competition_level:<12} {opportunity.score:<7.2f} {opportunity.recommendation:<10}")
            
            print("-"*100)
            
            # Show arbitrage opportunities
            arbitrage_opportunities = [o for o in analysis.best_opportunities if o.arbitrage_opportunity]
            if arbitrage_opportunities:
                print(f"\n🎯 ARBITRAGE OPPORTUNITIES ({len(arbitrage_opportunities)} found):")
                for opp in arbitrage_opportunities:
                    print(f"  - {opp.item_name}: Buy at {opp.avg_price_region:.2f} ISK, sell at {opp.avg_price_system:.2f} ISK")
        else:
            print("No profitable opportunities found in this system.")
    
    def export_system_analysis(self, analysis: SystemAnalysis, filename: str = None):
        """Export system analysis to JSON"""
        if filename is None:
            filename = f"system_analysis_{analysis.system_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'system_id': analysis.system_id,
            'system_name': analysis.system_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'total_opportunities': analysis.total_opportunities,
            'avg_profit_margin': analysis.avg_profit_margin,
            'market_activity': analysis.market_activity,
            'competition_level': analysis.competition_level,
            'recommended_items': analysis.recommended_items,
            'opportunities': [
                {
                    'type_id': o.type_id,
                    'item_name': o.item_name,
                    'current_price': o.current_price,
                    'avg_price_system': o.avg_price_system,
                    'avg_price_region': o.avg_price_region,
                    'price_difference': o.price_difference,
                    'profit_margin': o.profit_margin,
                    'volume_24h': o.volume_24h,
                    'competition_level': o.competition_level,
                    'market_depth': o.market_depth,
                    'arbitrage_opportunity': o.arbitrage_opportunity,
                    'score': o.score,
                    'recommendation': o.recommendation
                }
                for o in analysis.best_opportunities
            ]
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"System analysis exported to {filename}")

async def main():
    """Main function to run system trading analysis"""
    print("🎯 EVE System-Based Trading Analyzer")
    print("="*50)
    
    # Popular trading systems
    systems = [
        (60003760, "Jita"),
        (60008494, "Amarr"),
        (60011866, "Dodixie"),
        (60004588, "Rens"),
        (60005686, "Hek"),
        (60009106, "Oursulaert"),
        (60012721, "Niarja"),
        (60014995, "Perimeter"),
        (60015068, "New Caldari"),
        (60015169, "Old Man Star")
    ]
    
    print("Available systems:")
    for i, (system_id, system_name) in enumerate(systems, 1):
        print(f"  {i}. {system_name} (ID: {system_id})")
    
    # Analyze Jita by default (most profitable)
    target_system_id = 60003760  # Jita
    
    async with SystemTradingAnalyzer(target_system_id) as analyzer:
        analysis = await analyzer.analyze_system_opportunities(max_items=30)
        analyzer.display_system_analysis(analysis)
        analyzer.export_system_analysis(analysis)

if __name__ == "__main__":
    asyncio.run(main()) 
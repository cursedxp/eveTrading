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
    def __init__(self, target_system: str = "Jita"):
        self.target_system = target_system
        self.session = None
        self.db = SimpleDatabaseManager()
        
        # System-specific market characteristics
        self.system_profiles = {
            "Jita": {
                "competition": "Very High",
                "volume": "Very High", 
                "profit_margins": "Low",
                "specialization": "Everything",
                "best_items": ["Tritanium", "Pyerite", "Mexallon", "Isogen"]
            },
            "Amarr": {
                "competition": "High",
                "volume": "High",
                "profit_margins": "Medium",
                "specialization": "Minerals, Ships",
                "best_items": ["Tritanium", "Pyerite", "Mexallon", "Merlin", "Punisher"]
            },
            "Dodixie": {
                "competition": "Medium",
                "volume": "Medium",
                "profit_margins": "Medium-High",
                "specialization": "Minerals, Components",
                "best_items": ["Tritanium", "Pyerite", "Mechanical Parts", "Construction Blocks"]
            },
            "Rens": {
                "competition": "Medium",
                "volume": "Medium",
                "profit_margins": "Medium-High",
                "specialization": "Minerals, Ammunition",
                "best_items": ["Tritanium", "Antimatter Charge S", "Antimatter Charge M"]
            },
            "Hek": {
                "competition": "Medium",
                "volume": "Medium",
                "profit_margins": "Medium-High",
                "specialization": "Minerals, Drones",
                "best_items": ["Tritanium", "Warrior II", "Hammerhead II", "Ogre II"]
            }
        }
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_system_profile(self) -> Dict:
        """Get market profile for the target system"""
        return self.system_profiles.get(self.target_system, {
            "competition": "Unknown",
            "volume": "Unknown",
            "profit_margins": "Unknown",
            "specialization": "General",
            "best_items": ["Tritanium", "Pyerite"]
        })
    
    async def get_region_market_data(self, type_id: int, region_id: int = 10000002) -> List[Dict]:
        """Get market data for analysis"""
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
        current_buy_price = max(o['price'] for o in buy_orders)
        current_sell_price = min(o['price'] for o in sell_orders)
        profit_margin = (current_sell_price - current_buy_price) / current_buy_price if current_buy_price > 0 else 0
        
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
        
        # Create action plan
        if opportunity_type == "Undersupplied":
            action_plan = f"Buy {item['name']} from other systems and sell in {self.target_system}"
        elif opportunity_type == "Oversupplied":
            action_plan = f"Buy {item['name']} in {self.target_system} and sell in other systems"
        elif opportunity_type == "Arbitrage":
            action_plan = f"Buy low, sell high within {self.target_system} market"
        else:
            action_plan = f"Monitor {item['name']} for price movements"
        
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
            action_plan=action_plan
        )
    
    async def analyze_local_market(self, max_items: int = 30) -> LocalMarketAnalysis:
        """Analyze local market opportunities"""
        logger.info(f"Analyzing local market opportunities in {self.target_system}...")
        
        system_profile = self.get_system_profile()
        logger.info(f"System Profile: {system_profile['specialization']} market, {system_profile['competition']} competition")
        
        # Focus on system-specialized items
        specialized_items = system_profile.get('best_items', [])
        
        # Popular trading items with system focus
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
                    if opportunity and opportunity.score > 0.2:  # Lower threshold for local analysis
                        opportunities.append(opportunity)
                        analyzed_count += 1
                
                # Rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error analyzing {item['name']}: {e}")
                continue
        
        # Sort by score
        opportunities.sort(key=lambda x: x.score, reverse=True)
        
        # Calculate market health
        avg_profit_margin = np.mean([o.profit_margin for o in opportunities]) if opportunities else 0
        total_opportunities = len(opportunities)
        
        if avg_profit_margin > 0.15:
            market_health = "Excellent"
        elif avg_profit_margin > 0.10:
            market_health = "Good"
        elif avg_profit_margin > 0.05:
            market_health = "Fair"
        else:
            market_health = "Poor"
        
        # Identify market gaps
        market_gaps = []
        if not any(o.opportunity_type == "Undersupplied" for o in opportunities):
            market_gaps.append("No undersupplied items found")
        if not any(o.opportunity_type == "Arbitrage" for o in opportunities):
            market_gaps.append("Limited arbitrage opportunities")
        if avg_profit_margin < 0.05:
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
            avg_profit_margin=avg_profit_margin,
            market_health=market_health,
            competition_level=system_profile["competition"],
            best_opportunities=opportunities[:10],
            market_gaps=market_gaps,
            strategic_recommendations=strategic_recommendations
        )
    
    def display_local_analysis(self, analysis: LocalMarketAnalysis):
        """Display local market analysis results"""
        print(f"\n{'='*100}")
        print(f"LOCAL MARKET ANALYSIS: {analysis.system_name}")
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
    
    def export_local_analysis(self, analysis: LocalMarketAnalysis, filename: str = None):
        """Export local analysis to JSON"""
        if filename is None:
            filename = f"local_analysis_{analysis.system_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        data = {
            'system_name': analysis.system_name,
            'analysis_timestamp': datetime.now().isoformat(),
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
                    'action_plan': o.action_plan
                }
                for o in analysis.best_opportunities
            ]
        }
        
        import json
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Local analysis exported to {filename}")

async def main():
    """Main function to run local market analysis"""
    print("🎯 EVE Local Market Analyzer")
    print("="*50)
    
    # Available systems
    systems = ["Jita", "Amarr", "Dodixie", "Rens", "Hek"]
    
    print("Available systems:")
    for i, system in enumerate(systems, 1):
        print(f"  {i}. {system}")
    
    # Analyze Jita by default
    target_system = "Jita"
    
    async with LocalMarketAnalyzer(target_system) as analyzer:
        analysis = await analyzer.analyze_local_market(max_items=25)
        analyzer.display_local_analysis(analysis)
        analyzer.export_local_analysis(analysis)

if __name__ == "__main__":
    asyncio.run(main()) 
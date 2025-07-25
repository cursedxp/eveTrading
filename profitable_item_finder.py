"""
Profitable Item Finder - Analyzes market data to find profitable trading opportunities
Uses the EVE items database and real market data to identify the best items to trade
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from eve_items_database import EVE_ITEMS, get_trading_recommendations, get_item_by_id, EVEItem

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class ProfitabilityAnalysis:
    type_id: int
    item_name: str
    category: str
    current_price: float
    avg_price_7d: float
    avg_price_30d: float
    price_change_7d: float
    price_change_30d: float
    volume_24h: int
    volume_7d: int
    bid_ask_spread: float
    profit_margin: float
    volatility_score: float
    volume_score: float
    overall_score: float
    recommendation: str
    risk_level: str

class ProfitableItemFinder:
    def __init__(self, region_id: int = 10000002):  # The Forge
        self.region_id = region_id
        self.session = None
        self.analysis_results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_market_orders(self, type_id: int, order_type: str = "all") -> List[Dict]:
        """Fetch market orders for a specific item"""
        try:
            if order_type == "all":
                # Fetch both buy and sell orders
                sell_url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type=sell&type_id={type_id}"
                buy_url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type=buy&type_id={type_id}"
                
                async with self.session.get(sell_url) as sell_response, self.session.get(buy_url) as buy_response:
                    sell_orders = await sell_response.json() if sell_response.status == 200 else []
                    buy_orders = await buy_response.json() if buy_response.status == 200 else []
                    
                    # Add order type to each order
                    for order in sell_orders:
                        order['order_type'] = 'sell'
                    for order in buy_orders:
                        order['order_type'] = 'buy'
                    
                    return sell_orders + buy_orders
            else:
                url = f"https://esi.evetech.net/latest/markets/{self.region_id}/orders/?datasource=tranquility&order_type={order_type}&type_id={type_id}"
                async with self.session.get(url) as response:
                    if response.status == 200:
                        orders = await response.json()
                        for order in orders:
                            order['order_type'] = order_type
                        return orders
                    return []
        except Exception as e:
            logger.error(f"Error fetching market orders for type_id {type_id}: {e}")
            return []
    
    def calculate_profitability_metrics(self, orders: List[Dict], item: EVEItem) -> ProfitabilityAnalysis:
        """Calculate profitability metrics for an item"""
        if not orders:
            return None
            
        # Separate buy and sell orders
        sell_orders = [o for o in orders if o['order_type'] == 'sell']
        buy_orders = [o for o in orders if o['order_type'] == 'buy']
        
        if not sell_orders or not buy_orders:
            return None
        
        # Calculate current prices
        current_sell_price = min(o['price'] for o in sell_orders)
        current_buy_price = max(o['price'] for o in buy_orders)
        current_price = (current_sell_price + current_buy_price) / 2
        
        # Calculate bid-ask spread
        bid_ask_spread = (current_sell_price - current_buy_price) / current_price
        
        # Calculate volume (simplified - using order quantities)
        volume_24h = sum(o.get('volume_remain', 0) for o in orders)
        
        # Calculate price changes (simplified - would need historical data)
        price_change_7d = 0.05  # Placeholder - would need historical data
        price_change_30d = 0.10  # Placeholder
        
        # Calculate profit margin
        profit_margin = (current_sell_price - current_buy_price) / current_buy_price if current_buy_price > 0 else 0
        
        # Calculate scores
        volatility_score = min(1.0, abs(price_change_7d) * 10)  # Higher volatility = higher score
        volume_score = min(1.0, volume_24h / item.avg_volume)  # Higher volume = higher score
        
        # Overall score (weighted combination)
        overall_score = (
            profit_margin * 0.4 +
            volatility_score * 0.3 +
            volume_score * 0.3
        )
        
        # Determine recommendation
        if overall_score > 0.7:
            recommendation = "STRONG BUY"
            risk_level = "LOW"
        elif overall_score > 0.5:
            recommendation = "BUY"
            risk_level = "MEDIUM"
        elif overall_score > 0.3:
            recommendation = "HOLD"
            risk_level = "MEDIUM"
        else:
            recommendation = "SELL"
            risk_level = "HIGH"
        
        return ProfitabilityAnalysis(
            type_id=item.type_id,
            item_name=item.name,
            category=item.category,
            current_price=current_price,
            avg_price_7d=current_price * (1 + price_change_7d),
            avg_price_30d=current_price * (1 + price_change_30d),
            price_change_7d=price_change_7d,
            price_change_30d=price_change_30d,
            volume_24h=volume_24h,
            volume_7d=volume_24h * 7,  # Simplified
            bid_ask_spread=bid_ask_spread,
            profit_margin=profit_margin,
            volatility_score=volatility_score,
            volume_score=volume_score,
            overall_score=overall_score,
            recommendation=recommendation,
            risk_level=risk_level
        )
    
    async def analyze_item(self, item: EVEItem) -> Optional[ProfitabilityAnalysis]:
        """Analyze a single item for profitability"""
        try:
            logger.info(f"Analyzing {item.name} (ID: {item.type_id})...")
            orders = await self.fetch_market_orders(item.type_id)
            
            if not orders:
                logger.warning(f"No market data found for {item.name}")
                return None
            
            analysis = self.calculate_profitability_metrics(orders, item)
            if analysis:
                logger.info(f"Analysis complete for {item.name}: {analysis.recommendation} (Score: {analysis.overall_score:.2f})")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {item.name}: {e}")
            return None
    
    async def find_profitable_items(self, max_items: int = 20) -> List[ProfitabilityAnalysis]:
        """Find the most profitable items to trade"""
        logger.info("Starting profitable item analysis...")
        
        # Get recommended items from database
        recommended_items = get_trading_recommendations()[:max_items]
        
        # Analyze each item
        analyses = []
        for item in recommended_items:
            analysis = await self.analyze_item(item)
            if analysis:
                analyses.append(analysis)
        
        # Sort by overall score
        analyses.sort(key=lambda x: x.overall_score, reverse=True)
        
        self.analysis_results = analyses
        return analyses
    
    def display_analysis_results(self, top_n: int = 10):
        """Display analysis results in a formatted table"""
        if not self.analysis_results:
            print("No analysis results available.")
            return
        
        print("\n" + "="*100)
        print("PROFITABLE ITEM ANALYSIS RESULTS")
        print("="*100)
        print(f"{'Item Name':<25} {'Category':<15} {'Price':<10} {'Profit %':<10} {'Volume':<10} {'Score':<8} {'Rec':<10} {'Risk':<8}")
        print("-"*100)
        
        for analysis in self.analysis_results[:top_n]:
            print(f"{analysis.item_name:<25} {analysis.category:<15} {analysis.current_price:<10.2f} "
                  f"{analysis.profit_margin*100:<9.1f}% {analysis.volume_24h:<10} "
                  f"{analysis.overall_score:<7.2f} {analysis.recommendation:<10} {analysis.risk_level:<8}")
        
        print("-"*100)
        print(f"Analyzed {len(self.analysis_results)} items. Showing top {min(top_n, len(self.analysis_results))} results.")
    
    def export_analysis_to_csv(self, filename: str = "profitable_items_analysis.csv"):
        """Export analysis results to CSV"""
        if not self.analysis_results:
            logger.warning("No analysis results to export.")
            return
        
        df = pd.DataFrame([vars(analysis) for analysis in self.analysis_results])
        df.to_csv(filename, index=False)
        logger.info(f"Analysis results exported to {filename}")
    
    def get_best_trading_opportunities(self, min_score: float = 0.5) -> List[ProfitabilityAnalysis]:
        """Get the best trading opportunities above a minimum score"""
        return [analysis for analysis in self.analysis_results if analysis.overall_score >= min_score]

async def main():
    """Main function to run the profitable item finder"""
    print("🔍 EVE Profitable Item Finder")
    print("="*50)
    
    async with ProfitableItemFinder() as finder:
        # Find profitable items
        analyses = await finder.find_profitable_items(max_items=15)
        
        # Display results
        finder.display_analysis_results(top_n=10)
        
        # Export results
        finder.export_analysis_to_csv()
        
        # Get best opportunities
        best_opportunities = finder.get_best_trading_opportunities(min_score=0.6)
        print(f"\n🎯 Best Trading Opportunities (Score >= 0.6): {len(best_opportunities)} items")
        
        for analysis in best_opportunities[:5]:
            print(f"- {analysis.item_name}: {analysis.recommendation} (Score: {analysis.overall_score:.2f})")

if __name__ == "__main__":
    asyncio.run(main()) 
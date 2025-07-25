#!/usr/bin/env python3
"""
Automated Market Monitor for EVE Trading System
Provides real-time alerts and trading signals without violating EVE ToS
"""

import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import json
import time
from typing import Dict, List, Optional
from dataclasses import dataclass
from ai_trader import AdvancedAITrader
from database_simple import SimpleDatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automated_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TradingAlert:
    """Represents a trading alert"""
    timestamp: datetime
    item_name: str
    type_id: int
    alert_type: str  # 'BUY_SIGNAL', 'SELL_SIGNAL', 'PRICE_SPIKE', 'VOLUME_SPIKE'
    confidence: float
    current_price: float
    predicted_price: float
    message: str
    priority: str  # 'HIGH', 'MEDIUM', 'LOW'

class AutomatedMarketMonitor:
    """Automated market monitoring system with alerts"""
    
    def __init__(self):
        self.db_manager = SimpleDatabaseManager()
        self.ai_trader = AdvancedAITrader()
        self.base_url = "https://esi.evetech.net/latest"
        self.alerts = []
        self.monitored_items = {
            34: "Tritanium",
            35: "Pyerite",
            36: "Mexallon",
            37: "Isogen",
            38: "Nocxium",
            39: "Zydrine",
            40: "Megacyte"
        }
        self.alert_thresholds = {
            'price_spike': 0.10,  # 10% price change
            'volume_spike': 0.50,  # 50% volume change
            'confidence_threshold': 0.75,  # 75% confidence
            'arbitrage_threshold': 0.05   # 5% price difference
        }
        
    async def fetch_current_market_data(self, type_id: int, region_id: int = 10000002) -> List[Dict]:
        """Fetch current market data from EVE ESI API"""
        async with aiohttp.ClientSession() as session:
            try:
                # Fetch sell orders
                sell_url = f"{self.base_url}/markets/{region_id}/orders/"
                params = {'order_type': 'sell', 'type_id': type_id}
                async with session.get(sell_url, params=params) as response:
                    sell_orders = await response.json()
                
                # Fetch buy orders
                params = {'order_type': 'buy', 'type_id': type_id}
                async with session.get(sell_url, params=params) as response:
                    buy_orders = await response.json()
                
                # Add order type to each order
                for order in sell_orders:
                    order['order_type'] = 'sell'
                for order in buy_orders:
                    order['order_type'] = 'buy'
                
                return sell_orders + buy_orders
                
            except Exception as e:
                logger.error(f"Error fetching market data for type_id {type_id}: {e}")
                return []
    
    def analyze_price_movements(self, current_data: List[Dict], historical_data: pd.DataFrame) -> List[TradingAlert]:
        """Analyze price movements and generate alerts"""
        alerts = []
        
        if not current_data or historical_data.empty:
            return alerts
        
        # Calculate current market metrics
        current_prices = [order['price'] for order in current_data if order['order_type'] == 'sell']
        if not current_prices:
            return alerts
        
        current_avg_price = np.mean(current_prices)
        current_median_price = np.median(current_prices)
        
        # Get historical metrics
        historical_avg = historical_data['price'].mean()
        historical_std = historical_data['price'].std()
        
        # Check for price spikes
        price_change = abs(current_avg_price - historical_avg) / historical_avg
        if price_change > self.alert_thresholds['price_spike']:
            alert = TradingAlert(
                timestamp=datetime.now(),
                item_name=self.monitored_items.get(34, "Unknown"),
                type_id=34,
                alert_type="PRICE_SPIKE",
                confidence=min(price_change, 1.0),
                current_price=current_avg_price,
                predicted_price=historical_avg,
                message=f"Price spike detected! Current: {current_avg_price:.2f} ISK, Historical: {historical_avg:.2f} ISK",
                priority="HIGH" if price_change > 0.20 else "MEDIUM"
            )
            alerts.append(alert)
        
        return alerts
    
    def detect_arbitrage_opportunities(self, market_data: List[Dict]) -> List[TradingAlert]:
        """Detect arbitrage opportunities between buy and sell orders"""
        alerts = []
        
        if not market_data:
            return alerts
        
        # Separate buy and sell orders
        sell_orders = [order for order in market_data if order['order_type'] == 'sell']
        buy_orders = [order for order in market_data if order['order_type'] == 'buy']
        
        if not sell_orders or not buy_orders:
            return alerts
        
        # Find best prices
        best_sell_price = min(order['price'] for order in sell_orders)
        best_buy_price = max(order['price'] for order in buy_orders)
        
        # Calculate arbitrage opportunity
        if best_buy_price > best_sell_price:
            profit_margin = (best_buy_price - best_sell_price) / best_sell_price
            
            if profit_margin > self.alert_thresholds['arbitrage_threshold']:
                alert = TradingAlert(
                    timestamp=datetime.now(),
                    item_name=self.monitored_items.get(34, "Unknown"),
                    type_id=34,
                    alert_type="ARBITRAGE",
                    confidence=profit_margin,
                    current_price=best_sell_price,
                    predicted_price=best_buy_price,
                    message=f"Arbitrage opportunity! Buy at {best_sell_price:.2f} ISK, sell at {best_buy_price:.2f} ISK ({(profit_margin*100):.1f}% profit)",
                    priority="HIGH" if profit_margin > 0.10 else "MEDIUM"
                )
                alerts.append(alert)
        
        return alerts
    
    async def generate_ai_signals(self, type_id: int) -> List[TradingAlert]:
        """Generate AI trading signals"""
        alerts = []
        
        try:
            # Load and prepare data
            df = self.ai_trader.load_data(type_id, days=30)
            if df.empty:
                return alerts
            
            # Engineer features
            df = self.ai_trader.engineer_features(df)
            
            # Train models
            self.ai_trader.train_models(df)
            
            # Get predictions
            signals = self.ai_trader.predict_trading_signals(df, model_name='logistic_regression')
            
            # Convert signals to alerts
            for signal in signals:
                if signal.action in ['buy', 'sell'] and signal.confidence > self.alert_thresholds['confidence_threshold']:
                    alert = TradingAlert(
                        timestamp=datetime.now(),
                        item_name=self.monitored_items.get(type_id, "Unknown"),
                        type_id=type_id,
                        alert_type=f"{signal.action.upper()}_SIGNAL",
                        confidence=signal.confidence,
                        current_price=signal.current_price,
                        predicted_price=signal.predicted_price,
                        message=f"AI {signal.action.upper()} signal with {signal.confidence:.1%} confidence",
                        priority="HIGH" if signal.confidence > 0.85 else "MEDIUM"
                    )
                    alerts.append(alert)
        
        except Exception as e:
            logger.error(f"Error generating AI signals: {e}")
        
        return alerts
    
    async def monitor_market_cycle(self) -> List[TradingAlert]:
        """Run one complete market monitoring cycle"""
        all_alerts = []
        
        for type_id, item_name in self.monitored_items.items():
            logger.info(f"Monitoring {item_name} (Type ID: {type_id})")
            
            try:
                # Fetch current market data
                current_data = await self.fetch_current_market_data(type_id)
                
                # Load historical data
                historical_data = self.ai_trader.load_data(type_id, days=7)
                
                # Generate different types of alerts
                price_alerts = self.analyze_price_movements(current_data, historical_data)
                arbitrage_alerts = self.detect_arbitrage_opportunities(current_data)
                ai_alerts = await self.generate_ai_signals(type_id)
                
                # Combine all alerts
                cycle_alerts = price_alerts + arbitrage_alerts + ai_alerts
                all_alerts.extend(cycle_alerts)
                
                # Log summary
                logger.info(f"{item_name}: {len(cycle_alerts)} alerts generated")
                
            except Exception as e:
                logger.error(f"Error monitoring {item_name}: {e}")
        
        return all_alerts
    
    def display_alerts(self, alerts: List[TradingAlert]):
        """Display alerts in a formatted way"""
        if not alerts:
            print("🔍 No alerts generated in this cycle")
            return
        
        print(f"\n🚨 TRADING ALERTS ({len(alerts)} found)")
        print("=" * 60)
        
        for alert in alerts:
            priority_icon = "🔴" if alert.priority == "HIGH" else "🟡" if alert.priority == "MEDIUM" else "🟢"
            print(f"{priority_icon} {alert.alert_type} - {alert.item_name}")
            print(f"   Confidence: {alert.confidence:.1%}")
            print(f"   Current Price: {alert.current_price:.2f} ISK")
            print(f"   Message: {alert.message}")
            print(f"   Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 40)
    
    def save_alerts_to_file(self, alerts: List[TradingAlert], filename: str = "trading_alerts.json"):
        """Save alerts to a JSON file"""
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'timestamp': alert.timestamp.isoformat(),
                'item_name': alert.item_name,
                'type_id': alert.type_id,
                'alert_type': alert.alert_type,
                'confidence': alert.confidence,
                'current_price': alert.current_price,
                'predicted_price': alert.predicted_price,
                'message': alert.message,
                'priority': alert.priority
            })
        
        with open(filename, 'w') as f:
            json.dump(alert_data, f, indent=2)
        
        logger.info(f"Saved {len(alerts)} alerts to {filename}")
    
    async def run_continuous_monitoring(self, interval_minutes: int = 15, duration_hours: int = 24):
        """Run continuous market monitoring"""
        logger.info(f"Starting continuous monitoring (interval: {interval_minutes}min, duration: {duration_hours}h)")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        cycle_count = 0
        
        while datetime.now() < end_time:
            cycle_count += 1
            logger.info(f"Starting monitoring cycle {cycle_count}")
            
            try:
                # Run monitoring cycle
                alerts = await self.monitor_market_cycle()
                
                # Display and save alerts
                self.display_alerts(alerts)
                self.save_alerts_to_file(alerts, f"alerts_cycle_{cycle_count}.json")
                
                # Store alerts for summary
                self.alerts.extend(alerts)
                
                logger.info(f"Cycle {cycle_count} completed. {len(alerts)} alerts generated.")
                
                # Wait for next cycle
                if datetime.now() < end_time:
                    logger.info(f"Waiting {interval_minutes} minutes until next cycle...")
                    await asyncio.sleep(interval_minutes * 60)
                
            except Exception as e:
                logger.error(f"Error in monitoring cycle {cycle_count}: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
        
        # Final summary
        logger.info(f"Monitoring completed. Total cycles: {cycle_count}, Total alerts: {len(self.alerts)}")
        self.display_final_summary()
    
    def display_final_summary(self):
        """Display final monitoring summary"""
        print(f"\n📊 MONITORING SUMMARY")
        print("=" * 40)
        print(f"Total Alerts: {len(self.alerts)}")
        
        # Alert type breakdown
        alert_types = {}
        for alert in self.alerts:
            alert_types[alert.alert_type] = alert_types.get(alert.alert_type, 0) + 1
        
        print(f"Alert Types:")
        for alert_type, count in alert_types.items():
            print(f"  {alert_type}: {count}")
        
        # Priority breakdown
        priorities = {}
        for alert in self.alerts:
            priorities[alert.priority] = priorities.get(alert.priority, 0) + 1
        
        print(f"Priority Levels:")
        for priority, count in priorities.items():
            print(f"  {priority}: {count}")
        
        # High confidence alerts
        high_confidence = [a for a in self.alerts if a.confidence > 0.8]
        print(f"High Confidence Alerts (>80%): {len(high_confidence)}")

async def main():
    """Main function to run the automated monitor"""
    monitor = AutomatedMarketMonitor()
    
    print("🤖 AUTOMATED MARKET MONITOR")
    print("=" * 40)
    print("This system provides trading alerts and signals")
    print("All trades must be executed manually in-game")
    print("=" * 40)
    
    # Run continuous monitoring
    await monitor.run_continuous_monitoring(interval_minutes=15, duration_hours=2)

if __name__ == "__main__":
    asyncio.run(main()) 
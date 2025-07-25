import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import json
from database_simple import SimpleDatabaseManager
from ai_trader import AdvancedAITrader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MarketAlert:
    """Represents a market alert with details."""
    type_id: int
    item_name: str
    alert_type: str  # 'price_spike', 'volume_spike', 'ai_signal', 'arbitrage'
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    data: Dict

class MarketMonitor:
    """Real-time market monitoring system."""
    
    def __init__(self):
        self.db = SimpleDatabaseManager()
        self.ai_trader = AdvancedAITrader()
        self.base_url = "https://esi.evetech.net/latest"
        self.monitored_items = {
            34: "Tritanium",
            35: "Pyerite", 
            36: "Mexallon",
            37: "Isogen",
            38: "Nocxium",
            39: "Zydrine",
            40: "Megacyte"
        }
        self.price_history = {}
        self.alerts = []
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_current_market_data(self, type_id: int, region_id: int = 10000002) -> Optional[Dict]:
        """Fetch current market data for a specific item."""
        try:
            url = f"{self.base_url}/markets/{region_id}/orders/"
            params = {
                'type_id': type_id,
                'order_type': 'all'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    logger.error(f"Failed to fetch data for type_id {type_id}: {response.status}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching market data for type_id {type_id}: {e}")
            return None
    
    def analyze_price_movements(self, type_id: int, current_data: List[Dict]) -> List[MarketAlert]:
        """Analyze price movements and generate alerts."""
        alerts = []
        
        if not current_data:
            return alerts
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(current_data)
        df['issued'] = pd.to_datetime(df['issued'])
        
        # Calculate current statistics
        current_avg_price = df[df['is_buy_order'] == 0]['price'].mean()  # Sell orders only
        current_volume = df['volume_remain'].sum()
        
        # Get historical data for comparison
        historical_data = self.db.get_historical_orders(type_id, days=7)
        if not historical_data.empty:
            hist_avg_price = historical_data['price'].mean()
            hist_volume = historical_data['volume_remain'].sum()
            
            # Calculate price change percentage
            price_change_pct = ((current_avg_price - hist_avg_price) / hist_avg_price) * 100
            volume_change_pct = ((current_volume - hist_volume) / hist_volume) * 100
            
            # Generate alerts based on thresholds
            if abs(price_change_pct) > 10:
                alert_type = 'price_spike'
                severity = 'high' if abs(price_change_pct) > 20 else 'medium'
                message = f"Price {'increased' if price_change_pct > 0 else 'decreased'} by {abs(price_change_pct):.1f}%"
                
                alerts.append(MarketAlert(
                    type_id=type_id,
                    item_name=self.monitored_items.get(type_id, f"Item {type_id}"),
                    alert_type=alert_type,
                    message=message,
                    severity=severity,
                    timestamp=datetime.now(),
                    data={'price_change_pct': price_change_pct, 'current_price': current_avg_price}
                ))
            
            if abs(volume_change_pct) > 50:
                alert_type = 'volume_spike'
                severity = 'medium'
                message = f"Volume {'increased' if volume_change_pct > 0 else 'decreased'} by {abs(volume_change_pct):.1f}%"
                
                alerts.append(MarketAlert(
                    type_id=type_id,
                    item_name=self.monitored_items.get(type_id, f"Item {type_id}"),
                    alert_type=alert_type,
                    message=message,
                    severity=severity,
                    timestamp=datetime.now(),
                    data={'volume_change_pct': volume_change_pct, 'current_volume': current_volume}
                ))
        
        return alerts
    
    def detect_arbitrage_opportunities(self, type_id: int, current_data: List[Dict]) -> List[MarketAlert]:
        """Detect arbitrage opportunities between buy and sell orders."""
        alerts = []
        
        if not current_data:
            return alerts
        
        df = pd.DataFrame(current_data)
        
        # Separate buy and sell orders
        buy_orders = df[df['is_buy_order'] == 1].sort_values('price', ascending=False)
        sell_orders = df[df['is_buy_order'] == 0].sort_values('price', ascending=True)
        
        if not buy_orders.empty and not sell_orders.empty:
            best_buy_price = buy_orders.iloc[0]['price']
            best_sell_price = sell_orders.iloc[0]['price']
            
            # Calculate potential profit
            if best_buy_price > best_sell_price:
                profit_pct = ((best_buy_price - best_sell_price) / best_sell_price) * 100
                
                if profit_pct > 5:  # Only alert if profit > 5%
                    alerts.append(MarketAlert(
                        type_id=type_id,
                        item_name=self.monitored_items.get(type_id, f"Item {type_id}"),
                        alert_type='arbitrage',
                        message=f"Arbitrage opportunity: {profit_pct:.1f}% potential profit",
                        severity='high' if profit_pct > 10 else 'medium',
                        timestamp=datetime.now(),
                        data={
                            'best_buy_price': best_buy_price,
                            'best_sell_price': best_sell_price,
                            'profit_pct': profit_pct
                        }
                    ))
        
        return alerts
    
    async def generate_ai_signals(self, type_id: int) -> List[MarketAlert]:
        """Generate AI trading signals."""
        alerts = []
        
        try:
            # Load recent data for AI analysis
            df = self.ai_trader.load_data(type_id, days=30)
            if df.empty:
                return alerts
            
            # Engineer features and train models
            df_feat = self.ai_trader.engineer_features(df)
            accuracies = self.ai_trader.train_models(df_feat)
            
            if accuracies:
                best_model = max(accuracies, key=accuracies.get)
                signals = self.ai_trader.predict_trading_signals(df_feat, best_model)
                
                for signal in signals:
                    if signal.confidence > 0.7:  # Only high-confidence signals
                        alerts.append(MarketAlert(
                            type_id=type_id,
                            item_name=self.monitored_items.get(type_id, f"Item {type_id}"),
                            alert_type='ai_signal',
                            message=f"AI Signal: {signal.action.upper()} with {signal.confidence:.1%} confidence",
                            severity='high' if signal.confidence > 0.8 else 'medium',
                            timestamp=datetime.now(),
                            data={
                                'action': signal.action,
                                'confidence': signal.confidence,
                                'price': signal.price,
                                'model_used': signal.model_used
                            }
                        ))
        
        except Exception as e:
            logger.error(f"Error generating AI signals for type_id {type_id}: {e}")
        
        return alerts
    
    async def monitor_market(self, duration_minutes: int = 60) -> None:
        """Monitor market for specified duration."""
        logger.info(f"Starting market monitoring for {duration_minutes} minutes")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            logger.info("Fetching current market data...")
            
            for type_id, item_name in self.monitored_items.items():
                try:
                    # Fetch current data
                    current_data = await self.fetch_current_market_data(type_id)
                    
                    if current_data:
                        # Analyze price movements
                        price_alerts = self.analyze_price_movements(type_id, current_data)
                        self.alerts.extend(price_alerts)
                        
                        # Detect arbitrage opportunities
                        arbitrage_alerts = self.detect_arbitrage_opportunities(type_id, current_data)
                        self.alerts.extend(arbitrage_alerts)
                        
                        # Generate AI signals (less frequently to avoid API overload)
                        if len(self.alerts) % 5 == 0:  # Every 5th iteration
                            ai_alerts = await self.generate_ai_signals(type_id)
                            self.alerts.extend(ai_alerts)
                        
                        # Log significant alerts
                        for alert in price_alerts + arbitrage_alerts:
                            if alert.severity in ['high', 'critical']:
                                logger.warning(f"ALERT: {alert.message} for {alert.item_name}")
                    
                    # Small delay to avoid overwhelming the API
                    await asyncio.sleep(1)
                    
                except Exception as e:
                    logger.error(f"Error monitoring {item_name}: {e}")
            
            # Wait before next monitoring cycle
            await asyncio.sleep(30)  # Check every 30 seconds
        
        logger.info("Market monitoring completed")
    
    def get_alerts_summary(self) -> Dict:
        """Get a summary of all alerts."""
        if not self.alerts:
            return {"total_alerts": 0, "alerts_by_type": {}, "alerts_by_severity": {}}
        
        alerts_by_type = {}
        alerts_by_severity = {}
        
        for alert in self.alerts:
            # Count by type
            if alert.alert_type not in alerts_by_type:
                alerts_by_type[alert.alert_type] = 0
            alerts_by_type[alert.alert_type] += 1
            
            # Count by severity
            if alert.severity not in alerts_by_severity:
                alerts_by_severity[alert.severity] = 0
            alerts_by_severity[alert.severity] += 1
        
        return {
            "total_alerts": len(self.alerts),
            "alerts_by_type": alerts_by_type,
            "alerts_by_severity": alerts_by_severity,
            "recent_alerts": [alert for alert in self.alerts[-10:]]  # Last 10 alerts
        }
    
    def export_alerts_to_json(self, filename: str = "market_alerts.json") -> None:
        """Export alerts to JSON file."""
        alerts_data = []
        
        for alert in self.alerts:
            alerts_data.append({
                "type_id": alert.type_id,
                "item_name": alert.item_name,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "severity": alert.severity,
                "timestamp": alert.timestamp.isoformat(),
                "data": alert.data
            })
        
        with open(filename, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        
        logger.info(f"Exported {len(alerts_data)} alerts to {filename}")

async def main():
    """Main function to run the market monitor."""
    async with MarketMonitor() as monitor:
        print("🚀 Starting EVE Market Monitor")
        print("=" * 50)
        print("Monitoring items:")
        for type_id, name in monitor.monitored_items.items():
            print(f"  - {name} (ID: {type_id})")
        print("=" * 50)
        
        # Run monitoring for 10 minutes (adjust as needed)
        await monitor.monitor_market(duration_minutes=10)
        
        # Print summary
        summary = monitor.get_alerts_summary()
        print("\n📊 MONITORING SUMMARY")
        print("=" * 50)
        print(f"Total Alerts: {summary['total_alerts']}")
        print(f"Alerts by Type: {summary['alerts_by_type']}")
        print(f"Alerts by Severity: {summary['alerts_by_severity']}")
        
        # Export alerts
        monitor.export_alerts_to_json()
        
        # Show recent alerts
        if summary['recent_alerts']:
            print("\n🔔 RECENT ALERTS")
            print("=" * 50)
            for alert in summary['recent_alerts']:
                print(f"[{alert.severity.upper()}] {alert.item_name}: {alert.message}")

if __name__ == "__main__":
    asyncio.run(main()) 
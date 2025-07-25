import asyncio
import aiohttp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
import json
import time
from database_simple import SimpleDatabaseManager
from ai_trader import AdvancedAITrader
from market_monitor import MarketMonitor, MarketAlert
from portfolio_manager import PortfolioManager
import matplotlib.pyplot as plt

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedTradingSystem:
    """Integrated trading system combining AI, monitoring, and portfolio management."""
    
    def __init__(self, initial_capital: float = 1000000):
        self.db = SimpleDatabaseManager()
        self.ai_trader = AdvancedAITrader()
        self.portfolio_manager = PortfolioManager(initial_capital)
        self.base_url = "https://esi.evetech.net/latest"
        self.session = None
        
        # Trading configuration
        self.trading_enabled = False
        self.max_position_size = 0.1  # 10% of portfolio per position
        self.min_confidence_threshold = 0.7
        self.max_daily_trades = 10
        self.daily_trades = 0
        self.last_trade_date = None
        
        # Monitored items
        self.monitored_items = {
            34: "Tritanium",
            35: "Pyerite", 
            36: "Mexallon",
            37: "Isogen",
            38: "Nocxium",
            39: "Zydrine",
            40: "Megacyte"
        }
        
        # Performance tracking
        self.performance_history = []
        self.trading_signals = []
        
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_current_market_data(self, type_id: int, region_id: int = 10000002) -> Optional[List[Dict]]:
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
    
    def get_current_prices(self, market_data: List[Dict]) -> Dict[int, float]:
        """Extract current prices from market data."""
        prices = {}
        
        for type_id in self.monitored_items.keys():
            if market_data and any(order['type_id'] == type_id for order in market_data):
                # Get best sell price (lowest sell order)
                sell_orders = [order for order in market_data if order['type_id'] == type_id and order['is_buy_order'] == 0]
                if sell_orders:
                    best_sell_price = min(order['price'] for order in sell_orders)
                    prices[type_id] = best_sell_price
        
        return prices
    
    async def analyze_trading_opportunities(self) -> List[Dict]:
        """Analyze all monitored items for trading opportunities."""
        opportunities = []
        
        for type_id, item_name in self.monitored_items.items():
            try:
                # Fetch current market data
                market_data = await self.fetch_current_market_data(type_id)
                if not market_data:
                    continue
                
                # Load historical data for AI analysis
                df = self.ai_trader.load_data(type_id, days=30)
                if df.empty:
                    continue
                
                # Engineer features and train models
                df_feat = self.ai_trader.engineer_features(df)
                accuracies = self.ai_trader.train_models(df_feat)
                
                if not accuracies:
                    continue
                
                # Get AI signals
                best_model = max(accuracies, key=accuracies.get)
                signals = self.ai_trader.predict_trading_signals(df_feat, best_model)
                
                if signals:
                    signal = signals[0]
                    
                    # Get current market prices
                    current_prices = self.get_current_prices(market_data)
                    current_price = current_prices.get(type_id, 0)
                    
                    if current_price > 0 and signal.confidence >= self.min_confidence_threshold:
                        opportunity = {
                            'type_id': type_id,
                            'item_name': item_name,
                            'action': signal.action,
                            'confidence': signal.confidence,
                            'current_price': current_price,
                            'model_used': signal.model_used,
                            'model_accuracy': accuracies[best_model],
                            'timestamp': datetime.now()
                        }
                        opportunities.append(opportunity)
                
                # Small delay to avoid overwhelming the API
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error analyzing {item_name}: {e}")
        
        return opportunities
    
    def calculate_position_size(self, opportunity: Dict) -> int:
        """Calculate position size based on portfolio and risk management."""
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()
        available_cash = portfolio_summary['current_cash']
        
        # Calculate maximum position value
        max_position_value = portfolio_summary['total_portfolio_value'] * self.max_position_size
        
        # Calculate quantity based on current price
        quantity = int(max_position_value / opportunity['current_price'])
        
        # Ensure we don't exceed available cash
        max_quantity_by_cash = int(available_cash / opportunity['current_price'])
        quantity = min(quantity, max_quantity_by_cash)
        
        return max(0, quantity)
    
    def can_execute_trade(self, opportunity: Dict) -> bool:
        """Check if we can execute a trade based on constraints."""
        # Check daily trade limit
        today = datetime.now().date()
        if self.last_trade_date != today:
            self.daily_trades = 0
            self.last_trade_date = today
        
        if self.daily_trades >= self.max_daily_trades:
            logger.info("Daily trade limit reached")
            return False
        
        # Check if trading is enabled
        if not self.trading_enabled:
            logger.info("Trading is disabled")
            return False
        
        # Check confidence threshold
        if opportunity['confidence'] < self.min_confidence_threshold:
            logger.info(f"Confidence too low: {opportunity['confidence']:.3f}")
            return False
        
        return True
    
    async def execute_trade(self, opportunity: Dict) -> bool:
        """Execute a trade based on the opportunity."""
        if not self.can_execute_trade(opportunity):
            return False
        
        type_id = opportunity['type_id']
        action = opportunity['action']
        price = opportunity['current_price']
        
        if action == 'buy':
            quantity = self.calculate_position_size(opportunity)
            if quantity <= 0:
                logger.info(f"Insufficient funds for {opportunity['item_name']}")
                return False
            
            success = self.portfolio_manager.add_trade(type_id, 'buy', quantity, price)
            if success:
                self.daily_trades += 1
                logger.info(f"BUY: {quantity} {opportunity['item_name']} at {price:.2f} ISK")
                return True
        
        elif action == 'sell':
            # Check if we have holdings to sell
            portfolio_items = self.portfolio_manager.get_portfolio_items()
            holdings = next((item for item in portfolio_items if item.type_id == type_id), None)
            
            if holdings and holdings.quantity > 0:
                success = self.portfolio_manager.add_trade(type_id, 'sell', holdings.quantity, price)
                if success:
                    self.daily_trades += 1
                    logger.info(f"SELL: {holdings.quantity} {opportunity['item_name']} at {price:.2f} ISK")
                    return True
        
        return False
    
    async def update_portfolio_prices(self) -> None:
        """Update portfolio with current market prices."""
        all_prices = {}
        
        for type_id in self.monitored_items.keys():
            market_data = await self.fetch_current_market_data(type_id)
            if market_data:
                prices = self.get_current_prices(market_data)
                all_prices.update(prices)
            
            await asyncio.sleep(0.5)  # Small delay
        
        if all_prices:
            self.portfolio_manager.update_current_prices(all_prices)
    
    def record_performance(self) -> None:
        """Record current performance metrics."""
        summary = self.portfolio_manager.get_portfolio_summary()
        performance = self.portfolio_manager.get_performance_metrics()
        
        record = {
            'timestamp': datetime.now(),
            'portfolio_value': summary['total_portfolio_value'],
            'total_pnl': summary['total_pnl'],
            'total_return_pct': summary['total_return_pct'],
            'number_of_positions': summary['number_of_positions'],
            'number_of_trades': summary['number_of_trades']
        }
        
        if performance:
            record.update({
                'sharpe_ratio': performance.get('sharpe_ratio', 0),
                'max_drawdown': performance.get('max_drawdown', 0),
                'volatility': performance.get('volatility', 0)
            })
        
        self.performance_history.append(record)
    
    async def run_trading_cycle(self) -> None:
        """Run one complete trading cycle."""
        logger.info("Starting trading cycle...")
        
        # Update portfolio prices
        await self.update_portfolio_prices()
        
        # Analyze trading opportunities
        opportunities = await self.analyze_trading_opportunities()
        
        # Sort opportunities by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Execute trades for top opportunities
        trades_executed = 0
        for opportunity in opportunities:
            if trades_executed >= 3:  # Limit to 3 trades per cycle
                break
            
            if await self.execute_trade(opportunity):
                trades_executed += 1
                
                # Record the signal
                self.trading_signals.append({
                    'timestamp': opportunity['timestamp'],
                    'type_id': opportunity['type_id'],
                    'item_name': opportunity['item_name'],
                    'action': opportunity['action'],
                    'confidence': opportunity['confidence'],
                    'price': opportunity['current_price'],
                    'model_used': opportunity['model_used']
                })
        
        # Record performance
        self.record_performance()
        
        logger.info(f"Trading cycle completed. Trades executed: {trades_executed}")
    
    async def run_continuous_trading(self, duration_hours: int = 24) -> None:
        """Run continuous trading for specified duration."""
        logger.info(f"Starting continuous trading for {duration_hours} hours")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(hours=duration_hours)
        
        cycle_count = 0
        
        while datetime.now() < end_time:
            cycle_count += 1
            logger.info(f"Starting trading cycle {cycle_count}")
            
            try:
                await self.run_trading_cycle()
                
                # Print current status
                summary = self.portfolio_manager.get_portfolio_summary()
                print(f"\n📊 Cycle {cycle_count} Summary:")
                print(f"Portfolio Value: {summary['total_portfolio_value']:,.0f} ISK")
                print(f"Total P&L: {summary['total_pnl']:,.0f} ISK ({summary['total_return_pct']:.2f}%)")
                print(f"Positions: {summary['number_of_positions']}")
                print(f"Total Trades: {summary['number_of_trades']}")
                print("-" * 50)
                
            except Exception as e:
                logger.error(f"Error in trading cycle {cycle_count}: {e}")
            
            # Wait before next cycle (15 minutes)
            await asyncio.sleep(900)
        
        logger.info("Continuous trading completed")
    
    def get_system_summary(self) -> Dict:
        """Get comprehensive system summary."""
        portfolio_summary = self.portfolio_manager.get_portfolio_summary()
        performance_metrics = self.portfolio_manager.get_performance_metrics()
        
        return {
            "portfolio": portfolio_summary,
            "performance": performance_metrics,
            "trading_config": {
                "trading_enabled": self.trading_enabled,
                "max_position_size": self.max_position_size,
                "min_confidence_threshold": self.min_confidence_threshold,
                "max_daily_trades": self.max_daily_trades,
                "daily_trades": self.daily_trades
            },
            "monitored_items": self.monitored_items,
            "performance_history_count": len(self.performance_history),
            "trading_signals_count": len(self.trading_signals)
        }
    
    def export_system_report(self, filename: str = "trading_system_report.json") -> None:
        """Export comprehensive system report."""
        summary = self.get_system_summary()
        
        report = {
            "summary": summary,
            "performance_history": self.performance_history,
            "trading_signals": self.trading_signals,
            "portfolio_items": [
                {
                    "type_id": item.type_id,
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "avg_price": item.avg_price,
                    "current_price": item.current_price,
                    "current_value": item.current_value,
                    "unrealized_pnl": item.unrealized_pnl,
                    "unrealized_pnl_pct": item.unrealized_pnl_pct
                }
                for item in self.portfolio_manager.get_portfolio_items()
            ],
            "trade_history": [
                {
                    "trade_id": trade.trade_id,
                    "type_id": trade.type_id,
                    "item_name": trade.item_name,
                    "action": trade.action,
                    "quantity": trade.quantity,
                    "price": trade.price,
                    "total_value": trade.total_value,
                    "timestamp": trade.timestamp.isoformat()
                }
                for trade in self.portfolio_manager.get_trade_history()
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"System report exported to {filename}")
    
    def plot_system_performance(self) -> None:
        """Plot comprehensive system performance."""
        if not self.performance_history:
            print("No performance history to plot")
            return
        
        # Create performance DataFrame
        df = pd.DataFrame(self.performance_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp')
        
        # Create plots
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Portfolio value over time
        axes[0, 0].plot(df['timestamp'], df['portfolio_value'], marker='o', linewidth=2)
        axes[0, 0].set_title('Portfolio Value Over Time')
        axes[0, 0].set_xlabel('Time')
        axes[0, 0].set_ylabel('Portfolio Value (ISK)')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Total P&L over time
        axes[0, 1].plot(df['timestamp'], df['total_pnl'], marker='o', linewidth=2, color='green')
        axes[0, 1].set_title('Total P&L Over Time')
        axes[0, 1].set_xlabel('Time')
        axes[0, 1].set_ylabel('P&L (ISK)')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Number of positions over time
        axes[1, 0].plot(df['timestamp'], df['number_of_positions'], marker='o', linewidth=2, color='blue')
        axes[1, 0].set_title('Number of Positions Over Time')
        axes[1, 0].set_xlabel('Time')
        axes[1, 0].set_ylabel('Number of Positions')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Sharpe ratio over time (if available)
        if 'sharpe_ratio' in df.columns:
            axes[1, 1].plot(df['timestamp'], df['sharpe_ratio'], marker='o', linewidth=2, color='red')
            axes[1, 1].set_title('Sharpe Ratio Over Time')
            axes[1, 1].set_xlabel('Time')
            axes[1, 1].set_ylabel('Sharpe Ratio')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plt.show()

async def main():
    """Main function to run the integrated trading system."""
    async with IntegratedTradingSystem(initial_capital=1000000) as system:
        print("🚀 EVE Trading System")
        print("=" * 50)
        print("Initializing system...")
        
        # Enable trading (set to False for simulation only)
        system.trading_enabled = False  # Set to True for live trading
        
        # Run a few trading cycles for demonstration
        print("Running trading cycles...")
        for i in range(3):
            await system.run_trading_cycle()
            await asyncio.sleep(60)  # Wait 1 minute between cycles
        
        # Get final summary
        summary = system.get_system_summary()
        print("\n📊 FINAL SYSTEM SUMMARY")
        print("=" * 50)
        print(f"Portfolio Value: {summary['portfolio']['total_portfolio_value']:,.0f} ISK")
        print(f"Total P&L: {summary['portfolio']['total_pnl']:,.0f} ISK")
        print(f"Total Return: {summary['portfolio']['total_return_pct']:.2f}%")
        print(f"Positions: {summary['portfolio']['number_of_positions']}")
        print(f"Total Trades: {summary['portfolio']['number_of_trades']}")
        
        if summary['performance']:
            print(f"Sharpe Ratio: {summary['performance']['sharpe_ratio']:.4f}")
            print(f"Max Drawdown: {summary['performance']['max_drawdown']:.2%}")
        
        # Export report
        system.export_system_report()
        
        # Plot performance
        system.plot_system_performance()

if __name__ == "__main__":
    asyncio.run(main()) 
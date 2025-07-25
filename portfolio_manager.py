import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import json
from database_simple import SimpleDatabaseManager
import matplotlib.pyplot as plt
import seaborn as sns

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PortfolioItem:
    """Represents a portfolio item with holdings and metrics."""
    type_id: int
    item_name: str
    quantity: int
    avg_price: float
    current_price: float
    total_cost: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    last_updated: datetime

@dataclass
class Trade:
    """Represents a trade transaction."""
    trade_id: str
    type_id: int
    item_name: str
    action: str  # 'buy' or 'sell'
    quantity: int
    price: float
    total_value: float
    timestamp: datetime
    fees: float = 0.0

class PortfolioManager:
    """Comprehensive portfolio management system."""
    
    def __init__(self, initial_capital: float = 1000000):
        self.db = SimpleDatabaseManager()
        self.initial_capital = initial_capital
        self.current_cash = initial_capital
        self.portfolio = {}  # {type_id: PortfolioItem}
        self.trade_history = []
        self.item_names = {
            34: "Tritanium",
            35: "Pyerite", 
            36: "Mexallon",
            37: "Isogen",
            38: "Nocxium",
            39: "Zydrine",
            40: "Megacyte"
        }
        
    def add_trade(self, type_id: int, action: str, quantity: int, price: float, timestamp: datetime = None) -> bool:
        """Add a trade to the portfolio."""
        if timestamp is None:
            timestamp = datetime.now()
        
        if action not in ['buy', 'sell']:
            logger.error(f"Invalid action: {action}")
            return False
        
        if quantity <= 0 or price <= 0:
            logger.error(f"Invalid quantity or price: {quantity}, {price}")
            return False
        
        total_value = quantity * price
        fees = total_value * 0.01  # 1% trading fee
        
        # Create trade record
        trade = Trade(
            trade_id=f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{type_id}_{action}",
            type_id=type_id,
            item_name=self.item_names.get(type_id, f"Item {type_id}"),
            action=action,
            quantity=quantity,
            price=price,
            total_value=total_value,
            timestamp=timestamp,
            fees=fees
        )
        
        # Execute trade
        if action == 'buy':
            if self.current_cash < (total_value + fees):
                logger.error(f"Insufficient cash for buy order. Need: {total_value + fees}, Have: {self.current_cash}")
                return False
            
            # Deduct cash
            self.current_cash -= (total_value + fees)
            
            # Update portfolio
            if type_id not in self.portfolio:
                self.portfolio[type_id] = PortfolioItem(
                    type_id=type_id,
                    item_name=self.item_names.get(type_id, f"Item {type_id}"),
                    quantity=0,
                    avg_price=0,
                    current_price=price,
                    total_cost=0,
                    current_value=0,
                    unrealized_pnl=0,
                    unrealized_pnl_pct=0,
                    last_updated=timestamp
                )
            
            # Update holdings
            current_quantity = self.portfolio[type_id].quantity
            current_cost = self.portfolio[type_id].total_cost
            
            new_quantity = current_quantity + quantity
            new_cost = current_cost + total_value
            
            self.portfolio[type_id].quantity = new_quantity
            self.portfolio[type_id].avg_price = new_cost / new_quantity if new_quantity > 0 else 0
            self.portfolio[type_id].total_cost = new_cost
            self.portfolio[type_id].current_price = price
            self.portfolio[type_id].last_updated = timestamp
            
        elif action == 'sell':
            if type_id not in self.portfolio or self.portfolio[type_id].quantity < quantity:
                logger.error(f"Insufficient holdings for sell order. Need: {quantity}, Have: {self.portfolio.get(type_id, PortfolioItem(0, '', 0, 0, 0, 0, 0, 0, 0, datetime.now())).quantity}")
                return False
            
            # Add cash
            self.current_cash += (total_value - fees)
            
            # Update holdings
            current_quantity = self.portfolio[type_id].quantity
            current_cost = self.portfolio[type_id].total_cost
            
            new_quantity = current_quantity - quantity
            # Calculate cost basis for sold quantity
            sold_cost = (quantity / current_quantity) * current_cost if current_quantity > 0 else 0
            new_cost = current_cost - sold_cost
            
            self.portfolio[type_id].quantity = new_quantity
            self.portfolio[type_id].avg_price = new_cost / new_quantity if new_quantity > 0 else 0
            self.portfolio[type_id].total_cost = new_cost
            self.portfolio[type_id].current_price = price
            self.portfolio[type_id].last_updated = timestamp
            
            # Remove item if quantity becomes 0
            if new_quantity == 0:
                del self.portfolio[type_id]
        
        # Add to trade history
        self.trade_history.append(trade)
        
        # Update portfolio metrics
        self._update_portfolio_metrics()
        
        logger.info(f"Trade executed: {action.upper()} {quantity} {self.item_names.get(type_id, f'Item {type_id}')} at {price:.2f} ISK")
        return True
    
    def _update_portfolio_metrics(self) -> None:
        """Update portfolio metrics for all holdings."""
        for type_id, item in self.portfolio.items():
            if item.quantity > 0:
                item.current_value = item.quantity * item.current_price
                item.unrealized_pnl = item.current_value - item.total_cost
                item.unrealized_pnl_pct = (item.unrealized_pnl / item.total_cost) * 100 if item.total_cost > 0 else 0
    
    def update_current_prices(self, price_data: Dict[int, float]) -> None:
        """Update current prices for portfolio items."""
        for type_id, price in price_data.items():
            if type_id in self.portfolio:
                self.portfolio[type_id].current_price = price
                self.portfolio[type_id].last_updated = datetime.now()
        
        self._update_portfolio_metrics()
    
    def get_portfolio_summary(self) -> Dict:
        """Get comprehensive portfolio summary."""
        total_value = self.current_cash
        total_cost = 0
        total_unrealized_pnl = 0
        
        for item in self.portfolio.values():
            total_value += item.current_value
            total_cost += item.total_cost
            total_unrealized_pnl += item.unrealized_pnl
        
        total_realized_pnl = self._calculate_realized_pnl()
        total_pnl = total_unrealized_pnl + total_realized_pnl
        
        return {
            "initial_capital": self.initial_capital,
            "current_cash": self.current_cash,
            "total_portfolio_value": total_value,
            "total_cost": total_cost,
            "total_unrealized_pnl": total_unrealized_pnl,
            "total_realized_pnl": total_realized_pnl,
            "total_pnl": total_pnl,
            "total_return_pct": (total_pnl / self.initial_capital) * 100 if self.initial_capital > 0 else 0,
            "number_of_positions": len(self.portfolio),
            "number_of_trades": len(self.trade_history)
        }
    
    def _calculate_realized_pnl(self) -> float:
        """Calculate realized P&L from trade history."""
        realized_pnl = 0
        
        for trade in self.trade_history:
            if trade.action == 'sell':
                # Find corresponding buy trades to calculate realized P&L
                buy_trades = [t for t in self.trade_history if t.type_id == trade.type_id and t.action == 'buy' and t.timestamp < trade.timestamp]
                
                if buy_trades:
                    # Simplified calculation - in reality, you'd need FIFO/LIFO logic
                    avg_buy_price = sum(t.price * t.quantity for t in buy_trades) / sum(t.quantity for t in buy_trades)
                    realized_pnl += (trade.price - avg_buy_price) * trade.quantity
        
        return realized_pnl
    
    def get_portfolio_items(self) -> List[PortfolioItem]:
        """Get list of all portfolio items."""
        return list(self.portfolio.values())
    
    def get_trade_history(self, type_id: Optional[int] = None) -> List[Trade]:
        """Get trade history, optionally filtered by type_id."""
        if type_id is None:
            return self.trade_history
        else:
            return [trade for trade in self.trade_history if trade.type_id == type_id]
    
    def get_performance_metrics(self) -> Dict:
        """Calculate performance metrics."""
        if not self.trade_history:
            return {}
        
        # Calculate daily returns
        daily_returns = []
        portfolio_values = []
        dates = []
        
        # Group trades by date
        trades_by_date = {}
        for trade in self.trade_history:
            date = trade.timestamp.date()
            if date not in trades_by_date:
                trades_by_date[date] = []
            trades_by_date[date].append(trade)
        
        # Calculate portfolio value over time
        current_value = self.initial_capital
        for date in sorted(trades_by_date.keys()):
            for trade in trades_by_date[date]:
                if trade.action == 'buy':
                    current_value -= trade.total_value + trade.fees
                else:
                    current_value += trade.total_value - trade.fees
            
            portfolio_values.append(current_value)
            dates.append(date)
        
        # Calculate returns
        for i in range(1, len(portfolio_values)):
            daily_return = (portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1]
            daily_returns.append(daily_return)
        
        if not daily_returns:
            return {}
        
        # Calculate metrics
        avg_return = np.mean(daily_returns)
        volatility = np.std(daily_returns)
        sharpe_ratio = avg_return / volatility if volatility > 0 else 0
        
        # Calculate max drawdown
        peak = portfolio_values[0]
        max_drawdown = 0
        for value in portfolio_values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            max_drawdown = max(max_drawdown, drawdown)
        
        return {
            "avg_daily_return": avg_return,
            "volatility": volatility,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "total_return": (portfolio_values[-1] - self.initial_capital) / self.initial_capital if self.initial_capital > 0 else 0
        }
    
    def plot_portfolio_performance(self) -> None:
        """Plot portfolio performance over time."""
        if not self.trade_history:
            print("No trade history to plot")
            return
        
        # Group trades by date
        trades_by_date = {}
        for trade in self.trade_history:
            date = trade.timestamp.date()
            if date not in trades_by_date:
                trades_by_date[date] = []
            trades_by_date[date].append(trade)
        
        # Calculate portfolio value over time
        portfolio_values = []
        dates = []
        current_value = self.initial_capital
        
        for date in sorted(trades_by_date.keys()):
            for trade in trades_by_date[date]:
                if trade.action == 'buy':
                    current_value -= trade.total_value + trade.fees
                else:
                    current_value += trade.total_value - trade.fees
            
            portfolio_values.append(current_value)
            dates.append(date)
        
        # Create plot
        plt.figure(figsize=(15, 10))
        
        # Portfolio value over time
        plt.subplot(2, 2, 1)
        plt.plot(dates, portfolio_values, marker='o', linewidth=2, markersize=4)
        plt.axhline(y=self.initial_capital, color='r', linestyle='--', alpha=0.7, label='Initial Capital')
        plt.title('Portfolio Value Over Time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value (ISK)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Portfolio composition
        plt.subplot(2, 2, 2)
        if self.portfolio:
            labels = [item.item_name for item in self.portfolio.values()]
            sizes = [item.current_value for item in self.portfolio.values()]
            colors = plt.cm.Set3(np.linspace(0, 1, len(sizes)))
            
            plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors)
            plt.title('Current Portfolio Composition')
        
        # P&L by position
        plt.subplot(2, 2, 3)
        if self.portfolio:
            items = list(self.portfolio.values())
            names = [item.item_name for item in items]
            pnls = [item.unrealized_pnl for item in items]
            colors = ['green' if pnl >= 0 else 'red' for pnl in pnls]
            
            bars = plt.bar(names, pnls, color=colors, alpha=0.7)
            plt.title('Unrealized P&L by Position')
            plt.xlabel('Item')
            plt.ylabel('P&L (ISK)')
            plt.xticks(rotation=45)
            
            # Add value labels on bars
            for bar, pnl in zip(bars, pnls):
                plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (max(pnls) * 0.01),
                        f'{pnl:,.0f}', ha='center', va='bottom')
        
        # Trade activity
        plt.subplot(2, 2, 4)
        buy_trades = [t for t in self.trade_history if t.action == 'buy']
        sell_trades = [t for t in self.trade_history if t.action == 'sell']
        
        plt.hist([t.timestamp.date() for t in buy_trades], alpha=0.7, label='Buy Trades', bins=20)
        plt.hist([t.timestamp.date() for t in sell_trades], alpha=0.7, label='Sell Trades', bins=20)
        plt.title('Trade Activity Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Trades')
        plt.legend()
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.show()
    
    def export_portfolio_report(self, filename: str = "portfolio_report.json") -> None:
        """Export portfolio report to JSON."""
        summary = self.get_portfolio_summary()
        performance = self.get_performance_metrics()
        
        report = {
            "summary": summary,
            "performance_metrics": performance,
            "portfolio_items": [
                {
                    "type_id": item.type_id,
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "avg_price": item.avg_price,
                    "current_price": item.current_price,
                    "total_cost": item.total_cost,
                    "current_value": item.current_value,
                    "unrealized_pnl": item.unrealized_pnl,
                    "unrealized_pnl_pct": item.unrealized_pnl_pct,
                    "last_updated": item.last_updated.isoformat()
                }
                for item in self.portfolio.values()
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
                    "fees": trade.fees,
                    "timestamp": trade.timestamp.isoformat()
                }
                for trade in self.trade_history
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Portfolio report exported to {filename}")

def main():
    """Demo the portfolio manager."""
    # Create portfolio manager
    pm = PortfolioManager(initial_capital=1000000)
    
    # Simulate some trades
    print("🚀 Portfolio Manager Demo")
    print("=" * 50)
    
    # Buy some Tritanium
    pm.add_trade(34, 'buy', 1000, 5.50, datetime.now() - timedelta(days=5))
    pm.add_trade(34, 'buy', 500, 5.75, datetime.now() - timedelta(days=3))
    pm.add_trade(35, 'buy', 800, 3.20, datetime.now() - timedelta(days=2))
    
    # Sell some Tritanium
    pm.add_trade(34, 'sell', 300, 6.00, datetime.now() - timedelta(days=1))
    
    # Update current prices
    current_prices = {34: 6.25, 35: 3.45}
    pm.update_current_prices(current_prices)
    
    # Get summary
    summary = pm.get_portfolio_summary()
    print(f"Initial Capital: {summary['initial_capital']:,.0f} ISK")
    print(f"Current Cash: {summary['current_cash']:,.0f} ISK")
    print(f"Portfolio Value: {summary['total_portfolio_value']:,.0f} ISK")
    print(f"Total P&L: {summary['total_pnl']:,.0f} ISK ({summary['total_return_pct']:.2f}%)")
    print(f"Positions: {summary['number_of_positions']}")
    print(f"Trades: {summary['number_of_trades']}")
    
    # Show portfolio items
    print("\n📊 Portfolio Items:")
    print("=" * 50)
    for item in pm.get_portfolio_items():
        print(f"{item.item_name}:")
        print(f"  Quantity: {item.quantity:,}")
        print(f"  Avg Price: {item.avg_price:.2f} ISK")
        print(f"  Current Price: {item.current_price:.2f} ISK")
        print(f"  Unrealized P&L: {item.unrealized_pnl:,.0f} ISK ({item.unrealized_pnl_pct:.2f}%)")
        print()
    
    # Performance metrics
    performance = pm.get_performance_metrics()
    if performance:
        print("📈 Performance Metrics:")
        print("=" * 50)
        print(f"Avg Daily Return: {performance['avg_daily_return']:.4f}")
        print(f"Volatility: {performance['volatility']:.4f}")
        print(f"Sharpe Ratio: {performance['sharpe_ratio']:.4f}")
        print(f"Max Drawdown: {performance['max_drawdown']:.2%}")
        print(f"Total Return: {performance['total_return']:.2%}")
    
    # Export report
    pm.export_portfolio_report()
    
    # Plot performance
    pm.plot_portfolio_performance()

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Master Runner for EVE Trading System
====================================

This script provides a unified interface to run all components of the EVE trading system.
"""

import asyncio
import argparse
import sys
import logging
from datetime import datetime
from typing import Optional

# Import all system components
from fetchMarketData import main as fetch_data_main
from market_visualizer import MarketVisualizer
from web_dashboard import app as web_app
from ai_trader import AdvancedAITrader
from market_monitor import MarketMonitor
from portfolio_manager import PortfolioManager
from trading_system import IntegratedTradingSystem
from database_simple import SimpleDatabaseManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EVETradingMaster:
    """Master controller for the EVE Trading System."""
    
    def __init__(self):
        self.components = {
            'fetch_data': 'Fetch market data from EVE ESI API',
            'visualize': 'Generate market visualizations',
            'web_dashboard': 'Start web dashboard server',
            'ai_trader': 'Run AI trading analysis',
            'market_monitor': 'Start real-time market monitoring',
            'portfolio': 'Portfolio management demo',
            'trading_system': 'Run integrated trading system',
            'db_stats': 'Show database statistics'
        }
    
    def print_banner(self):
        """Print system banner."""
        print("=" * 60)
        print("🚀 EVE TRADING SYSTEM - MASTER CONTROLLER")
        print("=" * 60)
        print("Available Components:")
        for i, (component, description) in enumerate(self.components.items(), 1):
            print(f"  {i}. {component}: {description}")
        print("=" * 60)
    
    async def run_fetch_data(self, type_id: int = 34, item_name: str = "Tritanium"):
        """Run data fetching component."""
        print(f"📡 Fetching market data for {item_name} (ID: {type_id})...")
        await fetch_data_main()
        print("✅ Data fetching completed")
    
    def run_visualize(self):
        """Run visualization component."""
        print("📊 Generating market visualizations...")
        visualizer = MarketVisualizer()
        
        # Generate charts for Tritanium
        df = visualizer.load_data(34, "Tritanium")
        if not df.empty:
            visualizer.create_price_distribution(df, "Tritanium")
            visualizer.create_volume_price_scatter(df, "Tritanium")
            visualizer.create_market_depth_analysis(df, "Tritanium")
            visualizer.create_location_analysis(df, "Tritanium")
            visualizer.create_comprehensive_dashboard(df, "Tritanium")
            print("✅ Visualizations generated")
        else:
            print("❌ No data available for visualization")
    
    def run_web_dashboard(self, port: int = 5000):
        """Run web dashboard component."""
        print(f"🌐 Starting web dashboard on port {port}...")
        print(f"   Visit: http://localhost:{port}")
        print("   Press Ctrl+C to stop the server")
        
        try:
            web_app.run(host='0.0.0.0', port=port, debug=False)
        except KeyboardInterrupt:
            print("\n✅ Web dashboard stopped")
    
    def run_ai_trader(self):
        """Run AI trading analysis."""
        print("🤖 Running AI trading analysis...")
        trader = AdvancedAITrader()
        
        # Test with Tritanium
        results = trader.simulate_trading(34, days=90)
        
        if results:
            print("\n📊 AI TRADING RESULTS")
            print("=" * 40)
            print(f"Initial Value: {results['initial_value']:,.0f} ISK")
            print(f"Final Value: {results['final_value']:,.0f} ISK")
            print(f"Total Return: {results['total_return_pct']:.2f}%")
            print(f"Trades Made: {results['trades_made']}")
            print(f"Best Model: {results['best_model']}")
            print(f"Model Accuracy: {results['model_accuracy']:.3f}")
        else:
            print("❌ AI trading analysis failed")
    
    async def run_market_monitor(self, duration_minutes: int = 10):
        """Run market monitoring component."""
        print(f"🔍 Starting market monitoring for {duration_minutes} minutes...")
        
        async with MarketMonitor() as monitor:
            await monitor.monitor_market(duration_minutes=duration_minutes)
            
            summary = monitor.get_alerts_summary()
            print(f"\n📊 MONITORING SUMMARY")
            print(f"Total Alerts: {summary['total_alerts']}")
            print(f"Alerts by Type: {summary['alerts_by_type']}")
            print(f"Alerts by Severity: {summary['alerts_by_severity']}")
            
            monitor.export_alerts_to_json()
    
    def run_portfolio_demo(self):
        """Run portfolio management demo."""
        print("💼 Running portfolio management demo...")
        
        from portfolio_manager import main as portfolio_main
        portfolio_main()
    
    async def run_trading_system(self, cycles: int = 3):
        """Run integrated trading system."""
        print(f"🔄 Running integrated trading system ({cycles} cycles)...")
        
        async with IntegratedTradingSystem(initial_capital=1000000) as system:
            # Enable trading (set to False for simulation only)
            system.trading_enabled = False
            
            for i in range(cycles):
                print(f"\n🔄 Running cycle {i+1}/{cycles}...")
                await system.run_trading_cycle()
                await asyncio.sleep(30)  # Wait 30 seconds between cycles
            
            # Get final summary
            summary = system.get_system_summary()
            print(f"\n📊 FINAL SYSTEM SUMMARY")
            print(f"Portfolio Value: {summary['portfolio']['total_portfolio_value']:,.0f} ISK")
            print(f"Total P&L: {summary['portfolio']['total_pnl']:,.0f} ISK")
            print(f"Total Return: {summary['portfolio']['total_return_pct']:.2f}%")
            print(f"Positions: {summary['portfolio']['number_of_positions']}")
            print(f"Total Trades: {summary['portfolio']['number_of_trades']}")
            
            # Export report
            system.export_system_report()
    
    def show_db_stats(self):
        """Show database statistics."""
        print("🗄️ Database Statistics")
        print("=" * 40)
        
        db = SimpleDatabaseManager()
        
        # Get basic stats
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Count market orders
            cursor.execute("SELECT COUNT(*) FROM market_orders")
            order_count = cursor.fetchone()[0]
            
            # Count market analyses
            cursor.execute("SELECT COUNT(*) FROM market_analysis")
            analysis_count = cursor.fetchone()[0]
            
            # Get unique items
            cursor.execute("SELECT COUNT(DISTINCT type_id) FROM market_orders")
            unique_items = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("SELECT MIN(issued), MAX(issued) FROM market_orders")
            date_range = cursor.fetchone()
            
        print(f"Total Market Orders: {order_count:,}")
        print(f"Total Market Analyses: {analysis_count:,}")
        print(f"Unique Items Tracked: {unique_items}")
        
        if date_range[0] and date_range[1]:
            print(f"Data Range: {date_range[0]} to {date_range[1]}")
        
        # Show top items by volume
        print("\n📊 Top Items by Volume:")
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT type_id, SUM(volume_remain) as total_volume, COUNT(*) as order_count
                FROM market_orders 
                GROUP BY type_id 
                ORDER BY total_volume DESC 
                LIMIT 5
            """)
            
            for row in cursor.fetchall():
                type_id, volume, count = row
                item_name = {
                    34: "Tritanium",
                    35: "Pyerite",
                    36: "Mexallon"
                }.get(type_id, f"Item {type_id}")
                print(f"  {item_name}: {volume:,} units ({count} orders)")
    
    async def run_component(self, component: str, **kwargs):
        """Run a specific component."""
        if component == 'fetch_data':
            await self.run_fetch_data(**kwargs)
        elif component == 'visualize':
            self.run_visualize()
        elif component == 'web_dashboard':
            self.run_web_dashboard(**kwargs)
        elif component == 'ai_trader':
            self.run_ai_trader()
        elif component == 'market_monitor':
            await self.run_market_monitor(**kwargs)
        elif component == 'portfolio':
            self.run_portfolio_demo()
        elif component == 'trading_system':
            await self.run_trading_system(**kwargs)
        elif component == 'db_stats':
            self.show_db_stats()
        else:
            print(f"❌ Unknown component: {component}")
    
    async def run_all(self):
        """Run all components in sequence."""
        print("🚀 Running all components...")
        
        components = [
            ('fetch_data', {}),
            ('visualize', {}),
            ('ai_trader', {}),
            ('portfolio', {}),
            ('db_stats', {})
        ]
        
        for component, kwargs in components:
            print(f"\n{'='*20} {component.upper()} {'='*20}")
            try:
                await self.run_component(component, **kwargs)
            except Exception as e:
                print(f"❌ Error running {component}: {e}")
        
        print("\n✅ All components completed")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='EVE Trading System Master Controller')
    parser.add_argument('component', nargs='?', choices=['all'] + list(EVETradingMaster().components.keys()),
                       help='Component to run (or "all" for all components)')
    parser.add_argument('--type-id', type=int, default=34, help='Item type ID (default: 34 for Tritanium)')
    parser.add_argument('--item-name', default='Tritanium', help='Item name (default: Tritanium)')
    parser.add_argument('--port', type=int, default=5000, help='Web dashboard port (default: 5000)')
    parser.add_argument('--duration', type=int, default=10, help='Monitoring duration in minutes (default: 10)')
    parser.add_argument('--cycles', type=int, default=3, help='Trading cycles (default: 3)')
    
    args = parser.parse_args()
    
    master = EVETradingMaster()
    
    if not args.component:
        master.print_banner()
        print("\nUsage: python master_runner.py <component>")
        print("Example: python master_runner.py ai_trader")
        print("Example: python master_runner.py all")
        return
    
    try:
        if args.component == 'all':
            asyncio.run(master.run_all())
        else:
            kwargs = {
                'type_id': args.type_id,
                'item_name': args.item_name,
                'port': args.port,
                'duration_minutes': args.duration,
                'cycles': args.cycles
            }
            asyncio.run(master.run_component(args.component, **kwargs))
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
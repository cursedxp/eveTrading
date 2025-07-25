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
from profitable_item_finder import ProfitableItemFinder
from dynamic_item_discovery import DynamicItemDiscovery
from system_trading_analyzer import SystemTradingAnalyzer
from local_market_analyzer import LocalMarketAnalyzer
from jump_planner import JumpPlanner

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
            'db_stats': 'Show database statistics',
            'find_profitable': 'Find most profitable items to trade',
            'discover_items': 'Discover new profitable items using ESI API',
            'system_trading': 'Analyze trading opportunities in specific EVE systems',
            'local_market': 'Become the most profitable trader in your system',
            'jump_planning': 'Jump planning and transport efficiency analysis'
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
    
    async def run_fetch_data(self, type_id: int = 34, item_name: str = "Tritanium", **kwargs):
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
    
    async def run_profitable_finder(self, max_items: int = 15, **kwargs):
        """Run profitable item finder."""
        print("🔍 Finding most profitable items to trade...")
        
        async with ProfitableItemFinder() as finder:
            analyses = await finder.find_profitable_items(max_items=max_items)
            finder.display_analysis_results(top_n=10)
            finder.export_analysis_to_csv()
            
            best_opportunities = finder.get_best_trading_opportunities(min_score=0.5)
            print(f"\n🎯 Best Trading Opportunities (Score >= 0.5): {len(best_opportunities)} items")
            
            for analysis in best_opportunities[:5]:
                print(f"- {analysis.item_name}: {analysis.recommendation} (Score: {analysis.overall_score:.2f})")
        
        print("✅ Profitable item analysis completed")
    
    async def run_dynamic_discovery(self, min_score: float = 0.4, max_items: int = 30, **kwargs):
        """Run dynamic item discovery using ESI API."""
        print("🔍 Discovering new profitable items using ESI API...")
        
        async with DynamicItemDiscovery() as discoverer:
            # Discover profitable items
            items = await discoverer.discover_profitable_items(min_score=min_score, max_items=max_items)
            
            if items:
                # Display results
                discoverer.display_discovered_items(items, top_n=15)
                
                # Export results
                discoverer.export_discovered_items(items)
                
                # Update database
                results = await discoverer.update_database_with_discovered_items(items)
                
                print("\n📊 Database Update Results:")
                for item_name, count in results.items():
                    status = "✅ Success" if count > 0 else "❌ Failed"
                    print(f"  {item_name}: {count} orders ({status})")
                
                print(f"\n🎯 Discovered {len(items)} new profitable items!")
            else:
                print("No new profitable items discovered.")
        
        print("✅ Dynamic item discovery completed")
    
    async def run_system_trading_analysis(self, system_id: int = 60003760, max_items: int = 30, **kwargs):
        """Run system-based trading analysis."""
        print(f"🎯 Analyzing trading opportunities in system {system_id}...")
        
        async with SystemTradingAnalyzer(system_id) as analyzer:
            analysis = await analyzer.analyze_system_opportunities(max_items=max_items)
            analyzer.display_system_analysis(analysis)
            analyzer.export_system_analysis(analysis)
            
            print(f"\n🎯 System Analysis Complete!")
            print(f"📊 Found {analysis.total_opportunities} opportunities in {analysis.system_name}")
            print(f"💰 Average profit margin: {analysis.avg_profit_margin:.2%}")
            print(f"🏆 Competition level: {analysis.competition_level}")
            
            if analysis.best_opportunities:
                print(f"\n💎 Top 3 Opportunities:")
                for i, opp in enumerate(analysis.best_opportunities[:3], 1):
                    print(f"  {i}. {opp.item_name}: {opp.profit_margin*100:.1f}% profit (Score: {opp.score:.2f})")
        
        print("✅ System trading analysis completed")
    
    async def run_local_market_analysis(self, system_name: str = "Jita", max_items: int = 25, **kwargs):
        """Run local market analysis to become the most profitable trader in your system."""
        print(f"🎯 Analyzing local market opportunities in {system_name}...")
        
        async with LocalMarketAnalyzer(system_name) as analyzer:
            analysis = await analyzer.analyze_local_market(max_items=max_items)
            analyzer.display_local_analysis(analysis)
            analyzer.export_local_analysis(analysis)
            
            print(f"\n🎯 Local Market Analysis Complete!")
            print(f"📊 Found {analysis.total_opportunities} opportunities in {analysis.system_name}")
            print(f"💰 Average profit margin: {analysis.avg_profit_margin:.2%}")
            print(f"🏆 Market health: {analysis.market_health}")
            print(f"🎯 Competition level: {analysis.competition_level}")
            
            if analysis.best_opportunities:
                print(f"\n💎 Top 3 Local Opportunities:")
                for i, opp in enumerate(analysis.best_opportunities[:3], 1):
                    print(f"  {i}. {opp.item_name}: {opp.profit_margin*100:.1f}% profit ({opp.opportunity_type})")
            
            if analysis.strategic_recommendations:
                print(f"\n🎯 Key Strategies for {system_name}:")
                for i, rec in enumerate(analysis.strategic_recommendations[:3], 1):
                    print(f"  {i}. {rec}")
        
        print("✅ Local market analysis completed")
    
    def run_jump_planning(self, origin: str = "Jita", destination: str = "Amarr", 
                         cargo_volume: float = 500000, item_name: str = "Warrior II",
                         quantity: int = 1000, buy_price: float = 4050, 
                         sell_price: float = 5000):
        """Run jump planning and transport efficiency analysis."""
        print("🚀 Running jump planning and transport efficiency analysis...")
        
        planner = JumpPlanner()
        
        # Route analysis
        print(f"\n📍 ROUTE ANALYSIS: {origin} → {destination}")
        planner.display_route_analysis(origin, destination, cargo_volume)
        
        # Transport efficiency analysis
        print(f"\n📦 TRANSPORT EFFICIENCY ANALYSIS")
        efficiency = planner.analyze_transport_efficiency(
            item_name=item_name,
            quantity=quantity,
            buy_price=buy_price,
            sell_price=sell_price,
            origin=origin,
            destination=destination
        )
        planner.display_transport_efficiency(efficiency)
        
        # Ship comparison for different routes
        print(f"\n🔄 SHIP COMPARISON FOR MULTIPLE ROUTES")
        routes = [
            ("Jita", "Dodixie", 200000),
            ("Amarr", "Hek", 800000),
            ("Dodixie", "Rens", 300000)
        ]
        
        for route_origin, route_dest, route_volume in routes:
            print(f"\n📍 {route_origin} → {route_dest} ({route_volume:,} m³)")
            planner.display_route_analysis(route_origin, route_dest, route_volume)
        
        print("✅ Jump planning analysis completed")
    
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
        elif component == 'find_profitable':
            await self.run_profitable_finder(**kwargs)
        elif component == 'discover_items':
            await self.run_dynamic_discovery(**kwargs)
        elif component == 'system_trading':
            await self.run_system_trading_analysis(**kwargs)
        elif component == 'local_market':
            await self.run_local_market_analysis(**kwargs)
        elif component == 'jump_planning':
            self.run_jump_planning(
                origin=kwargs.get('origin', 'Jita'),
                destination=kwargs.get('destination', 'Amarr'),
                cargo_volume=kwargs.get('cargo_volume', 500000),
                item_name=kwargs.get('item_name', 'Warrior II'),
                quantity=kwargs.get('quantity', 1000),
                buy_price=kwargs.get('buy_price', 4050),
                sell_price=kwargs.get('sell_price', 5000)
            )
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
    parser.add_argument('--item-name', default='Tritanium', help='Item name (default: Tritanium)', nargs='+')
    parser.add_argument('--port', type=int, default=5000, help='Web dashboard port (default: 5000)')
    parser.add_argument('--duration', type=int, default=10, help='Monitoring duration in minutes (default: 10)')
    parser.add_argument('--cycles', type=int, default=3, help='Trading cycles (default: 3)')
    parser.add_argument('--system_id', type=int, default=60003760, help='Target system ID for analysis')
    parser.add_argument('--system_name', type=str, default='Jita', help='Target system name for local analysis')
    parser.add_argument('--max_items', type=int, default=30, help='Maximum items to analyze')
    parser.add_argument('--min_score', type=float, default=0.4, help='Minimum score threshold')
    parser.add_argument('--origin', type=str, default='Jita', help='Origin system for jump planning')
    parser.add_argument('--destination', type=str, default='Amarr', help='Destination system for jump planning')
    parser.add_argument('--cargo_volume', type=float, default=500000, help='Cargo volume in m³')
    parser.add_argument('--quantity', type=int, default=1000, help='Item quantity for transport analysis')
    parser.add_argument('--buy_price', type=float, default=4050, help='Buy price for transport analysis')
    parser.add_argument('--sell_price', type=float, default=5000, help='Sell price for transport analysis')
    
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
                'item_name': ' '.join(args.item_name) if isinstance(args.item_name, list) else args.item_name,
                'port': args.port,
                'duration_minutes': args.duration,
                'cycles': args.cycles,
                'system_id': args.system_id,
                'system_name': args.system_name,
                'max_items': args.max_items,
                'min_score': args.min_score,
                'origin': args.origin,
                'destination': args.destination,
                'cargo_volume': args.cargo_volume,
                'quantity': args.quantity,
                'buy_price': args.buy_price,
                'sell_price': args.sell_price
            }
            asyncio.run(master.run_component(args.component, **kwargs))
    
    except KeyboardInterrupt:
        print("\n⏹️ Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
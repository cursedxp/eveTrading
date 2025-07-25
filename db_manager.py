#!/usr/bin/env python3
"""
Database Management Script for EVE Trading Market Analysis Tool.
Provides advanced database operations and maintenance utilities.
"""

import argparse
import pandas as pd
from datetime import datetime, timedelta
import logging
from database_simple import SimpleDatabaseManager as DatabaseManager
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def show_database_stats(db_manager: DatabaseManager):
    """Display comprehensive database statistics."""
    print("\n📊 Database Statistics")
    print("=" * 50)
    
    stats = db_manager.get_database_stats()
    
    print(f"Total Market Orders: {stats['total_orders']:,}")
    print(f"Total Market Analyses: {stats['total_analyses']:,}")
    print(f"Unique Items Tracked: {stats['unique_items']:,}")
    
    if stats['oldest_order']:
        print(f"Oldest Order: {stats['oldest_order'].strftime('%Y-%m-%d %H:%M:%S')}")
    if stats['newest_order']:
        print(f"Newest Order: {stats['newest_order'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Calculate data age
    if stats['oldest_order'] and stats['newest_order']:
        age_days = (stats['newest_order'] - stats['oldest_order']).days
        print(f"Data Span: {age_days} days")

def show_top_items(db_manager: DatabaseManager, limit: int = 10):
    """Display top items by trading volume."""
    print(f"\n🏆 Top {limit} Items by Volume")
    print("=" * 50)
    
    top_items = db_manager.get_top_items_by_volume(limit)
    
    if top_items.empty:
        print("No analysis data available.")
        return
    
    for idx, row in top_items.iterrows():
        print(f"{idx + 1:2d}. Type ID {int(row['type_id']):6d} | "
              f"Volume: {int(row['total_volume']):12,} | "
              f"Avg Price: {float(row['avg_price']):8.2f} ISK | "
              f"Orders: {int(row['total_orders']):4d}")

def show_market_trends(db_manager: DatabaseManager, type_id: int, days: int = 30):
    """Display market trends for a specific item."""
    print(f"\n📈 Market Trends for Type ID {type_id} (Last {days} days)")
    print("=" * 60)
    
    trends = db_manager.get_market_trends(type_id, days)
    
    if trends.empty:
        print("No trend data available for this item.")
        return
    
    print(f"{'Date':<12} {'Orders':<8} {'Avg Price':<12} {'Volume':<12} {'Locations':<10}")
    print("-" * 60)
    
    for _, row in trends.iterrows():
        date_str = row['analysis_date'][:10] if isinstance(row['analysis_date'], str) else row['analysis_date'].strftime('%Y-%m-%d')
        print(f"{date_str:<12} {int(row['total_orders']):<8} "
              f"{float(row['avg_price']):<12.2f} {int(row['total_volume']):<12,} "
              f"{int(row['unique_locations']):<10}")

def cleanup_old_data(db_manager: DatabaseManager, days: int = 90):
    """Clean up old market data."""
    print(f"\n🧹 Cleaning up data older than {days} days...")
    
    deleted_count = db_manager.cleanup_old_data(days)
    
    if deleted_count > 0:
        print(f"✅ Deleted {deleted_count:,} old market orders")
    else:
        print("✅ No old data to clean up")

def export_data(db_manager: DatabaseManager, type_id: int, output_file: str):
    """Export market data to CSV."""
    print(f"\n📤 Exporting data for Type ID {type_id}...")
    
    # Get historical data
    historical_data = db_manager.get_historical_orders(type_id, days=365)
    
    if historical_data.empty:
        print("No data available for export.")
        return
    
    # Export to CSV
    historical_data.to_csv(output_file, index=False)
    print(f"✅ Exported {len(historical_data):,} records to {output_file}")

def show_item_details(db_manager: DatabaseManager, type_id: int):
    """Show detailed information about a specific item."""
    print(f"\n🔍 Item Details for Type ID {type_id}")
    print("=" * 50)
    
    # Get recent orders
    recent_orders = db_manager.get_market_orders(type_id, limit=5)
    
    if recent_orders.empty:
        print("No recent orders found for this item.")
        return
    
    print("Recent Orders:")
    print(f"{'Order ID':<10} {'Price':<12} {'Volume':<12} {'Location':<10} {'Type':<6}")
    print("-" * 60)
    
    for _, order in recent_orders.iterrows():
        print(f"{int(order['order_id']):<10} {float(order['price']):<12.2f} "
              f"{int(order['volume_remain']):<12,} {int(order['location_id']):<10} "
              f"{order['order_type']:<6}")

def main():
    """Main function for database management."""
    parser = argparse.ArgumentParser(description='EVE Trading Database Manager')
    parser.add_argument('command', choices=[
        'stats', 'top-items', 'trends', 'cleanup', 'export', 'details'
    ], help='Command to execute')
    
    parser.add_argument('--type-id', type=int, help='Item type ID for specific operations')
    parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    parser.add_argument('--limit', type=int, default=10, help='Limit for top items')
    parser.add_argument('--output', type=str, help='Output file for export')
    
    args = parser.parse_args()
    
    # Initialize database manager
    db_manager = DatabaseManager()
    
    try:
        if args.command == 'stats':
            show_database_stats(db_manager)
            
        elif args.command == 'top-items':
            show_top_items(db_manager, args.limit)
            
        elif args.command == 'trends':
            if not args.type_id:
                print("Error: --type-id is required for trends command")
                return
            show_market_trends(db_manager, args.type_id, args.days)
            
        elif args.command == 'cleanup':
            cleanup_old_data(db_manager, args.days)
            
        elif args.command == 'export':
            if not args.type_id:
                print("Error: --type-id is required for export command")
                return
            if not args.output:
                args.output = f"market_data_{args.type_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            export_data(db_manager, args.type_id, args.output)
            
        elif args.command == 'details':
            if not args.type_id:
                print("Error: --type-id is required for details command")
                return
            show_item_details(db_manager, args.type_id)
            
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 
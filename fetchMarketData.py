import os
import aiohttp
import pandas as pd
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime
import asyncio
from market_visualizer import MarketVisualizer
from database_simple import SimpleDatabaseManager as DatabaseManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

BASE_URL = os.getenv('BASE_URL')
if not BASE_URL:
    raise ValueError("BASE_URL environment variable is required")

async def fetch_market_orders(
    region_id: int = 10000002, 
    type_id: Optional[int] = None, 
    order_type: str = "sell"
) -> List[Dict[str, Any]]:
    
    if order_type not in ["sell", "buy"]:
        raise ValueError("order_type must be 'sell' or 'buy'")
    
    url = f"{BASE_URL}/markets/{region_id}/orders/"
    params = {
        "order_type": order_type,
        "page": 1,
    }

    if type_id:
        params["type_id"] = type_id
    
    logger.info(f"Fetching {order_type} orders for region {region_id}")
    if type_id:
        logger.info(f"Filtering by type_id: {type_id}")
    
    try:
        # Use aiohttp for async HTTP requests
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
                response.raise_for_status()
                orders = await response.json()
                logger.info(f"Successfully fetched {len(orders)} orders")
                return orders
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch market orders: {e}")
        raise

async def fetch_multiple_market_orders(
    type_ids: List[int],
    region_id: int = 10000002,
    order_type: str = "sell"
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Fetch market orders for multiple items concurrently
    This demonstrates concurrent async operations
    """
    async with aiohttp.ClientSession() as session:
        tasks = []
        for type_id in type_ids:
            task = fetch_market_orders_for_session(session, region_id, type_id, order_type)
            tasks.append(task)
        
        # Execute all requests concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        market_data = {}
        for type_id, result in zip(type_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch data for type_id {type_id}: {result}")
                market_data[type_id] = []
            else:
                market_data[type_id] = result
        
        return market_data

async def fetch_market_orders_for_session(
    session: aiohttp.ClientSession,
    region_id: int,
    type_id: int,
    order_type: str
) -> List[Dict[str, Any]]:
    """Helper function for concurrent requests using shared session"""
    url = f"{BASE_URL}/markets/{region_id}/orders/"
    params = {
        "order_type": order_type,
        "page": 1,
        "type_id": type_id
    }
    
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        logger.error(f"Failed to fetch market orders for type_id {type_id}: {e}")
        raise

def analyze_market_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze market data - this function is synchronous since pandas operations are CPU-bound
    """
    if df.empty:
        return {"error": "No data to analyze"}
    
    # Calculate volume-weighted average price
    volume_weighted_avg_price = (df['price'] * df['volume_remain']).sum() / df['volume_remain'].sum()
    
    analysis = {
        "total_orders": len(df),
        "avg_price": df['price'].mean(),
        "median_price": df['price'].median(),
        "min_price": df['price'].min(),
        "max_price": df['price'].max(),
        "total_volume": df['volume_remain'].sum(),
        "unique_locations": df['location_id'].nunique(),
        "price_std": df['price'].std(),
        "volume_weighted_avg_price": volume_weighted_avg_price,
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    return analysis

async def main():
    """Main function to demonstrate market data fetching and analysis."""
    try:
        # Single item fetch
        type_id = 34
        logger.info("Starting EVE market data analysis")
        
        orders = await fetch_market_orders(type_id=type_id)
        df = pd.DataFrame(orders)
        
        if df.empty:
            logger.warning("No market orders found")
            return
        
        # Display basic info
        print(f"\n📊 Market Data Analysis for Tritanium (Type ID: {type_id})")
        print("=" * 60)
        print(f"Total Orders: {len(df)}")
        print(f"Average Price: {df['price'].mean():,.2f} ISK")
        print(f"Price Range: {df['price'].min():,.2f} - {df['price'].max():,.2f} ISK")
        print(f"Total Volume: {df['volume_remain'].sum():,} units")
        
        # Show sample data
        print(f"\n📋 Sample Orders (Top 5):")
        print(df[['price', 'volume_remain', 'location_id', 'issued']].head())
        
        # Initialize database
        db_manager = DatabaseManager()
        
        # Store market orders in database
        print(f"\n💾 Storing Data in Database...")
        stored_count = db_manager.store_market_orders(orders, type_id)
        print(f"  ✅ Stored {stored_count} market orders")
        
        # Store market analysis
        analysis = analyze_market_data(df)
        db_manager.store_market_analysis(analysis, type_id)
        print(f"  ✅ Stored market analysis")
        
        # Display analysis
        print(f"\n🔍 Detailed Analysis:")
        for key, value in analysis.items():
            if key != "analysis_timestamp":
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # Get database statistics
        db_stats = db_manager.get_database_stats()
        print(f"\n📊 Database Statistics:")
        print(f"  Total Orders: {db_stats['total_orders']:,}")
        print(f"  Total Analyses: {db_stats['total_analyses']:,}")
        print(f"  Unique Items: {db_stats['unique_items']:,}")
        
        # Generate visualizations
        print(f"\n📊 Generating Market Visualizations...")
        visualizer = MarketVisualizer()
        charts = visualizer.generate_all_charts(df, "Tritanium")
        
        print(f"\n🎨 Generated Charts:")
        for chart_type, filepath in charts.items():
            print(f"  📈 {chart_type.replace('_', ' ').title()}: {filepath}")
        
        # Example of concurrent fetching (uncomment to test)
        # print(f"\n🚀 Concurrent Market Data Fetching:")
        # type_ids = [34, 35, 36]  # Tritanium, Pyerite, Mexallon
        # concurrent_data = await fetch_multiple_market_orders(type_ids)
        # for type_id, orders in concurrent_data.items():
        #     print(f"Type ID {type_id}: {len(orders)} orders")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())



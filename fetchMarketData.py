import os
import requests
import pandas as pd
from dotenv import load_dotenv
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

BASE_URL = os.getenv('BASE_URL')
if not BASE_URL:
    raise ValueError("BASE_URL environment variable is required")

def fetch_market_orders(
    region_id: int = 10000002, 
    type_id: Optional[int] = None, 
    order_type: str = "sell"
) -> List[Dict[str, Any]]:
    """
    Fetch market orders from EVE Online ESI API.
    
    Args:
        region_id: The region ID to fetch orders from (default: 10000002 for Forge)
        type_id: The item type ID to filter by (optional)
        order_type: Type of orders to fetch ("sell" or "buy")
    
    Returns:
        List of market order dictionaries
    
    Raises:
        requests.RequestException: If the API request fails
        ValueError: If invalid parameters are provided
    """
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
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        orders = response.json()
        logger.info(f"Successfully fetched {len(orders)} orders")
        return orders
    except requests.RequestException as e:
        logger.error(f"Failed to fetch market orders: {e}")
        raise

def analyze_market_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Analyze market data and return key statistics.
    
    Args:
        df: DataFrame containing market orders
    
    Returns:
        Dictionary with market analysis
    """
    if df.empty:
        return {"error": "No data to analyze"}
    
    analysis = {
        "total_orders": len(df),
        "avg_price": df['price'].mean(),
        "min_price": df['price'].min(),
        "max_price": df['price'].max(),
        "total_volume": df['volume_remain'].sum(),
        "unique_locations": df['location_id'].nunique(),
        "analysis_timestamp": datetime.now().isoformat()
    }
    
    return analysis

def main():
    """Main function to demonstrate market data fetching and analysis."""
    try:
        # Fetch market data for Tritanium (type_id: 34)
        type_id = 34
        logger.info("Starting EVE market data analysis")
        
        orders = fetch_market_orders(type_id=type_id)
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
        
        # Detailed analysis
        analysis = analyze_market_data(df)
        print(f"\n🔍 Detailed Analysis:")
        for key, value in analysis.items():
            if key != "analysis_timestamp":
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()



import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime
import os

# Configure matplotlib for better output
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

logger = logging.getLogger(__name__)

class MarketVisualizer:
    """
    Comprehensive data visualization class for EVE Online market data.
    
    This class provides various visualization methods for analyzing market data
    including price distributions, volume analysis, and market trends.
    """
    
    def __init__(self, output_dir: str = "charts"):
        """
        Initialize the MarketVisualizer.
        
        Args:
            output_dir: Directory to save generated charts
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Set up the plotting style
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        
    def create_price_distribution(self, df: pd.DataFrame, item_name: str = "Item") -> str:
        """
        Create a price distribution histogram with statistics.
        
        Args:
            df: DataFrame containing market data
            item_name: Name of the item for the title
            
        Returns:
            Path to saved chart
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Filter out extreme outliers for better visualization
        price_data = df['price']
        q1, q3 = price_data.quantile([0.25, 0.75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        filtered_prices = price_data[(price_data >= lower_bound) & (price_data <= upper_bound)]
        
        # Main histogram
        ax1.hist(filtered_prices, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(filtered_prices.mean(), color='red', linestyle='--', 
                   label=f'Mean: {filtered_prices.mean():.2f}')
        ax1.axvline(filtered_prices.median(), color='green', linestyle='--', 
                   label=f'Median: {filtered_prices.median():.2f}')
        ax1.set_xlabel('Price (ISK)')
        ax1.set_ylabel('Frequency')
        ax1.set_title(f'{item_name} - Price Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Box plot
        ax2.boxplot(filtered_prices, vert=False)
        ax2.set_xlabel('Price (ISK)')
        ax2.set_title(f'{item_name} - Price Box Plot')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the chart
        filename = f"{self.output_dir}/price_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Price distribution chart saved: {filename}")
        return filename
    
    def create_volume_price_scatter(self, df: pd.DataFrame, item_name: str = "Item") -> str:
        """
        Create a scatter plot of volume vs price.
        
        Args:
            df: DataFrame containing market data
            item_name: Name of the item for the title
            
        Returns:
            Path to saved chart
        """
        plt.figure(figsize=(12, 8))
        
        # Create scatter plot with size based on volume
        plt.scatter(df['price'], df['volume_remain'], 
                   alpha=0.6, s=df['volume_remain']/10000, c=df['price'], 
                   cmap='viridis')
        
        plt.colorbar(label='Price (ISK)')
        plt.xlabel('Price (ISK)')
        plt.ylabel('Volume Remaining')
        plt.title(f'{item_name} - Volume vs Price Analysis')
        plt.grid(True, alpha=0.3)
        
        # Add trend line
        z = np.polyfit(df['price'], df['volume_remain'], 1)
        p = np.poly1d(z)
        plt.plot(df['price'], p(df['price']), "r--", alpha=0.8, 
                label=f'Trend line')
        plt.legend()
        
        filename = f"{self.output_dir}/volume_price_scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Volume-price scatter chart saved: {filename}")
        return filename
    
    def create_market_depth_analysis(self, df: pd.DataFrame, item_name: str = "Item") -> str:
        """
        Create a market depth analysis showing cumulative volume at different price levels.
        
        Args:
            df: DataFrame containing market data
            item_name: Name of the item for the title
            
        Returns:
            Path to saved chart
        """
        # Sort by price and calculate cumulative volume
        sorted_df = df.sort_values('price')
        sorted_df['cumulative_volume'] = sorted_df['volume_remain'].cumsum()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Market depth curve
        ax1.plot(sorted_df['price'], sorted_df['cumulative_volume'], 
                linewidth=2, color='blue')
        ax1.fill_between(sorted_df['price'], sorted_df['cumulative_volume'], 
                        alpha=0.3, color='blue')
        ax1.set_xlabel('Price (ISK)')
        ax1.set_ylabel('Cumulative Volume')
        ax1.set_title(f'{item_name} - Market Depth')
        ax1.grid(True, alpha=0.3)
        
        # Volume distribution by price ranges
        price_bins = pd.cut(sorted_df['price'], bins=10)
        volume_by_price = sorted_df.groupby(price_bins)['volume_remain'].sum()
        
        ax2.bar(range(len(volume_by_price)), volume_by_price.values, 
               color='orange', alpha=0.7)
        ax2.set_xlabel('Price Range')
        ax2.set_ylabel('Total Volume')
        ax2.set_title(f'{item_name} - Volume by Price Range')
        ax2.set_xticks(range(len(volume_by_price)))
        ax2.set_xticklabels([f'{int(x.left):.0f}-{int(x.right):.0f}' 
                            for x in volume_by_price.index], rotation=45)
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/market_depth_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Market depth analysis chart saved: {filename}")
        return filename
    
    def create_location_analysis(self, df: pd.DataFrame, item_name: str = "Item") -> str:
        """
        Create analysis of market activity by location.
        
        Args:
            df: DataFrame containing market data
            item_name: Name of the item for the title
            
        Returns:
            Path to saved chart
        """
        # Analyze top locations by volume
        location_stats = df.groupby('location_id').agg({
            'volume_remain': 'sum',
            'price': 'mean',
            'order_id': 'count'
        }).rename(columns={'order_id': 'order_count'})
        
        top_locations = location_stats.nlargest(10, 'volume_remain')
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Top locations by volume
        ax1.barh(range(len(top_locations)), top_locations['volume_remain'], 
                color='lightcoral')
        ax1.set_yticks(range(len(top_locations)))
        ax1.set_yticklabels([f'Location {loc}' for loc in top_locations.index])
        ax1.set_xlabel('Total Volume')
        ax1.set_title('Top 10 Locations by Volume')
        ax1.grid(True, alpha=0.3)
        
        # Average price by location
        ax2.barh(range(len(top_locations)), top_locations['price'], 
                color='lightblue')
        ax2.set_yticks(range(len(top_locations)))
        ax2.set_yticklabels([f'Location {loc}' for loc in top_locations.index])
        ax2.set_xlabel('Average Price (ISK)')
        ax2.set_title('Average Price by Location')
        ax2.grid(True, alpha=0.3)
        
        # Order count by location
        ax3.barh(range(len(top_locations)), top_locations['order_count'], 
                color='lightgreen')
        ax3.set_yticks(range(len(top_locations)))
        ax3.set_yticklabels([f'Location {loc}' for loc in top_locations.index])
        ax3.set_xlabel('Number of Orders')
        ax3.set_title('Order Count by Location')
        ax3.grid(True, alpha=0.3)
        
        # Scatter plot: Volume vs Price by location
        ax4.scatter(location_stats['price'], location_stats['volume_remain'], 
                   alpha=0.6, s=location_stats['order_count']*10)
        ax4.set_xlabel('Average Price (ISK)')
        ax4.set_ylabel('Total Volume')
        ax4.set_title('Volume vs Price by Location')
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        filename = f"{self.output_dir}/location_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Location analysis chart saved: {filename}")
        return filename
    
    def create_comprehensive_dashboard(self, df: pd.DataFrame, item_name: str = "Item") -> str:
        """
        Create a comprehensive dashboard with multiple visualizations.
        
        Args:
            df: DataFrame containing market data
            item_name: Name of the item for the title
            
        Returns:
            Path to saved chart
        """
        fig = plt.figure(figsize=(20, 16))
        
        # Create a grid layout
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Price distribution (top left)
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.hist(df['price'], bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.axvline(df['price'].mean(), color='red', linestyle='--', 
                   label=f'Mean: {df["price"].mean():.2f}')
        ax1.set_title('Price Distribution')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. Volume distribution (top center)
        ax2 = fig.add_subplot(gs[0, 1])
        ax2.hist(df['volume_remain'], bins=30, alpha=0.7, color='lightgreen', edgecolor='black')
        ax2.set_title('Volume Distribution')
        ax2.grid(True, alpha=0.3)
        
        # 3. Price vs Volume scatter (top right)
        ax3 = fig.add_subplot(gs[0, 2])
        scatter = ax3.scatter(df['price'], df['volume_remain'], 
                            alpha=0.6, c=df['price'], cmap='viridis')
        ax3.set_xlabel('Price (ISK)')
        ax3.set_ylabel('Volume')
        ax3.set_title('Price vs Volume')
        plt.colorbar(scatter, ax=ax3)
        
        # 4. Box plot (middle left)
        ax4 = fig.add_subplot(gs[1, 0])
        ax4.boxplot(df['price'], vert=False)
        ax4.set_xlabel('Price (ISK)')
        ax4.set_title('Price Box Plot')
        ax4.grid(True, alpha=0.3)
        
        # 5. Market depth (middle center)
        ax5 = fig.add_subplot(gs[1, 1])
        sorted_df = df.sort_values('price')
        sorted_df['cumulative_volume'] = sorted_df['volume_remain'].cumsum()
        ax5.plot(sorted_df['price'], sorted_df['cumulative_volume'], linewidth=2)
        ax5.set_xlabel('Price (ISK)')
        ax5.set_ylabel('Cumulative Volume')
        ax5.set_title('Market Depth')
        ax5.grid(True, alpha=0.3)
        
        # 6. Volume by price range (middle right)
        ax6 = fig.add_subplot(gs[1, 2])
        price_bins = pd.cut(df['price'], bins=8)
        volume_by_price = df.groupby(price_bins)['volume_remain'].sum()
        ax6.bar(range(len(volume_by_price)), volume_by_price.values, color='orange')
        ax6.set_xlabel('Price Range')
        ax6.set_ylabel('Total Volume')
        ax6.set_title('Volume by Price Range')
        ax6.set_xticks(range(len(volume_by_price)))
        ax6.set_xticklabels([f'{int(x.left):.0f}-{int(x.right):.0f}' 
                            for x in volume_by_price.index], rotation=45)
        
        # 7. Statistics summary (bottom row)
        ax7 = fig.add_subplot(gs[2, :])
        ax7.axis('off')
        
        # Create statistics text
        stats_text = f"""
        Market Analysis Summary for {item_name}
        
        Total Orders: {len(df):,}
        Average Price: {df['price'].mean():,.2f} ISK
        Median Price: {df['price'].median():,.2f} ISK
        Price Range: {df['price'].min():,.2f} - {df['price'].max():,.2f} ISK
        Total Volume: {df['volume_remain'].sum():,} units
        Unique Locations: {df['location_id'].nunique()}
        
        Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        ax7.text(0.1, 0.5, stats_text, fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8),
                verticalalignment='center')
        
        plt.suptitle(f'EVE Market Analysis Dashboard - {item_name}', fontsize=16, y=0.95)
        
        filename = f"{self.output_dir}/comprehensive_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Comprehensive dashboard saved: {filename}")
        return filename
    
    def generate_all_charts(self, df: pd.DataFrame, item_name: str = "Item") -> Dict[str, str]:
        """
        Generate all available charts for the given data.
        
        Args:
            df: DataFrame containing market data
            item_name: Name of the item for the title
            
        Returns:
            Dictionary mapping chart type to file path
        """
        charts = {}
        
        try:
            charts['price_distribution'] = self.create_price_distribution(df, item_name)
            charts['volume_price_scatter'] = self.create_volume_price_scatter(df, item_name)
            charts['market_depth'] = self.create_market_depth_analysis(df, item_name)
            charts['location_analysis'] = self.create_location_analysis(df, item_name)
            charts['comprehensive_dashboard'] = self.create_comprehensive_dashboard(df, item_name)
            
            logger.info(f"Generated {len(charts)} charts for {item_name}")
            
        except Exception as e:
            logger.error(f"Error generating charts: {e}")
            raise
        
        return charts

def main():
    """Demo function to test the visualizer."""
    # This would be called from your main script
    visualizer = MarketVisualizer()
    print("MarketVisualizer initialized successfully!")
    print("Use this class in your main script to generate charts.")

if __name__ == "__main__":
    main() 
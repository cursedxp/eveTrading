import pandas as pd
import numpy as np
from database_simple import SimpleDatabaseManager
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from typing import Tuple, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import asyncio
from local_market_analyzer import LocalMarketAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TradingSignal:
    """Represents a trading signal with confidence and metadata."""
    action: str  # 'buy', 'sell', 'hold'
    confidence: float
    price: float
    volume: int
    timestamp: datetime
    features: Dict[str, float]
    model_used: str
    # System-based fields
    buy_location: Optional[str] = None
    sell_location: Optional[str] = None
    profit_margin: Optional[float] = None
    transport_cost: Optional[float] = None
    net_profit_percent: Optional[float] = None
    opportunity_type: Optional[str] = None  # 'Undersupplied', 'Oversupplied', 'Arbitrage', 'Stable'
    local_demand: Optional[str] = None
    local_supply: Optional[str] = None
    competition_level: Optional[str] = None
    action_plan: Optional[str] = None

class AdvancedAITrader:
    """Advanced AI trading system with multiple models and simulation."""
    
    def __init__(self):
        self.db = SimpleDatabaseManager()
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_columns = []
        self.trading_history = []
        self.portfolio_value = 1000000  # Starting with 1M ISK
        self.portfolio = {}  # {type_id: {'quantity': int, 'avg_price': float}}
        
        # System-based trading configuration
        self.target_system = ""  # No default system
        self.system_regions = {
            "Jita": 10000002,  # Forge
            "Amarr": 10000043,  # Domain
            "Dodixie": 10000032,  # Essence
            "Rens": 10000030,  # Heimatar
            "Hek": 10000042,  # Metropolis
        }
        
    def set_target_system(self, system_name: str):
        """Set the target system for system-based trading."""
        if system_name in self.system_regions:
            self.target_system = system_name
            logger.info(f"Target system set to: {system_name}")
        else:
            logger.warning(f"Unknown system: {system_name}. Using default: {self.target_system}")
    
    def load_data(self, type_id: int, days: int = 180) -> pd.DataFrame:
        """Load historical market data."""
        logger.info(f"Loading historical data for type_id {type_id}")
        df = self.db.get_historical_orders(type_id, days)
        if df.empty:
            logger.error(f"No data found for type_id {type_id}")
            return pd.DataFrame()
        
        df = df.sort_values('issued')
        df['issued'] = pd.to_datetime(df['issued'])
        return df
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Create advanced features for ML models."""
        df = df.copy()
        
        # Basic price features
        df['price_ma7'] = df['price'].rolling(window=7).mean()
        df['price_ma21'] = df['price'].rolling(window=21).mean()
        df['price_ma50'] = df['price'].rolling(window=50).mean()
        
        # Volatility features
        df['volatility_7'] = df['price'].rolling(window=7).std()
        df['volatility_21'] = df['price'].rolling(window=21).std()
        
        # Volume features
        df['volume_ma7'] = df['volume_remain'].rolling(window=7).mean()
        df['volume_ma21'] = df['volume_remain'].rolling(window=21).mean()
        
        # Price momentum
        df['price_change_1d'] = df['price'].pct_change(1)
        df['price_change_7d'] = df['price'].pct_change(7)
        df['price_change_21d'] = df['price'].pct_change(21)
        
        # Technical indicators
        df['rsi'] = self._calculate_rsi(df['price'], window=14)
        df['bollinger_upper'] = df['price_ma21'] + (df['volatility_21'] * 2)
        df['bollinger_lower'] = df['price_ma21'] - (df['volatility_21'] * 2)
        df['bollinger_position'] = (df['price'] - df['bollinger_lower']) / (df['bollinger_upper'] - df['bollinger_lower'])
        
        # Market depth features (if available)
        df['bid_ask_spread'] = df['price'] * 0.01  # Simplified spread calculation
        
        # Target: 1 if price goes up significantly tomorrow, 0 otherwise
        df['target'] = (df['price'].shift(-1) > df['price'] * 1.01).astype(int)
        
        # Remove NaN values
        df = df.dropna()
        
        # Store feature columns for later use
        self.feature_columns = [col for col in df.columns if col not in ['target', 'issued', 'order_id', 'type_id', 'location_id', 'region_id', 'order_type', 'duration', 'is_buy_order', 'min_volume', 'range']]
        
        return df
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train multiple ML models and return accuracies."""
        if df.empty or len(df) < 50:
            logger.error("Insufficient data for training")
            return {}
        
        # Prepare features and target
        X = df[self.feature_columns].values
        y = df['target'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features for SVM
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define models
        models = {
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'svm': SVC(probability=True, random_state=42)
        }
        
        accuracies = {}
        
        for name, model in models.items():
            logger.info(f"Training {name}...")
            
            # Train model
            if name == 'svm':
                model.fit(X_train_scaled, y_train)
                y_pred = model.predict(X_test_scaled)
            else:
                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)
            
            # Calculate accuracy
            accuracy = accuracy_score(y_test, y_pred)
            accuracies[name] = accuracy
            
            # Store model
            self.models[name] = model
            
            logger.info(f"{name} accuracy: {accuracy:.3f}")
        
        return accuracies
    
    async def find_most_profitable_routes(self, type_id: int, item_name: str) -> List[TradingSignal]:
        """Find the most profitable trading routes across multiple systems."""
        signals = []
        
        try:
            # Define major trading systems to analyze
            trading_systems = ["Jita", "Amarr", "Dodixie", "Rens", "Hek"]
            
            # Load historical data for AI analysis
            df = self.load_data(type_id, days=30)
            if df.empty:
                return signals
            
            # Engineer features and train models
            df_feat = self.engineer_features(df)
            accuracies = self.train_models(df_feat)
            
            if not accuracies:
                return signals
            
            # Get AI prediction
            best_model = max(accuracies, key=accuracies.get)
            ai_signals = self.predict_trading_signals(df_feat, best_model)
            
            if not ai_signals:
                return signals
            
            ai_signal = ai_signals[0]
            
            # Analyze opportunities across all systems
            system_opportunities = []
            
            for system in trading_systems:
                try:
                    async with LocalMarketAnalyzer(system) as analyzer:
                        # Get market data for this specific item
                        orders = await analyzer.get_region_market_data(type_id)
                        
                        if orders:
                            # Analyze local opportunity
                            item_info = {'type_id': type_id, 'name': item_name}
                            system_profile = analyzer.get_system_profile()
                            opportunity = analyzer.analyze_local_opportunity(orders, item_info, system_profile)
                            
                            if opportunity and opportunity.score > 0.2:
                                system_opportunities.append({
                                    'system': system,
                                    'opportunity': opportunity,
                                    'system_profile': system_profile
                                })
                
                except Exception as e:
                    logger.error(f"Error analyzing {system}: {e}")
                    continue
            
            # Find the most profitable routes
            profitable_routes = []
            
            for i, source_opp in enumerate(system_opportunities):
                for j, target_opp in enumerate(system_opportunities):
                    if i != j:  # Don't compare system with itself
                        source_system = source_opp['system']
                        target_system = target_opp['system']
                        
                        # Calculate cross-system profit
                        buy_price = source_opp['opportunity'].current_buy_price
                        sell_price = target_opp['opportunity'].current_sell_price
                        
                        if buy_price > 0 and sell_price > 0:
                            gross_profit = sell_price - buy_price
                            profit_margin = gross_profit / buy_price if buy_price > 0 else 0
                            
                            # Estimate transport cost (simplified)
                            transport_cost = 100.0  # Base transport cost
                            
                            # Adjust transport cost based on distance and system characteristics
                            # Use system volume and competition to determine transport costs
                            source_volume = self.trading_systems.get(source_system, {}).get("volume", "Medium")
                            target_volume = self.trading_systems.get(target_system, {}).get("volume", "Medium")
                            
                            # Higher volume systems typically have better transport infrastructure
                            if source_volume == "Very High" and target_volume != "Very High":
                                transport_cost = 150.0  # Export from high-volume hub
                            elif target_volume == "Very High" and source_volume != "Very High":
                                transport_cost = 150.0  # Import to high-volume hub
                            elif source_volume == "High" and target_volume == "High":
                                transport_cost = 180.0  # Between high-volume systems
                            else:
                                transport_cost = 200.0  # Default for other routes
                            
                            net_profit = gross_profit - transport_cost
                            net_profit_percent = (net_profit / buy_price) * 100 if buy_price > 0 else 0
                            
                            # Only consider profitable routes
                            if net_profit_percent > 5.0:  # Minimum 5% net profit
                                profitable_routes.append({
                                    'buy_system': source_system,
                                    'sell_system': target_system,
                                    'buy_price': buy_price,
                                    'sell_price': sell_price,
                                    'gross_profit': gross_profit,
                                    'profit_margin': profit_margin,
                                    'transport_cost': transport_cost,
                                    'net_profit': net_profit,
                                    'net_profit_percent': net_profit_percent,
                                    'source_opportunity': source_opp['opportunity'],
                                    'target_opportunity': target_opp['opportunity']
                                })
            
            # Sort by net profit percentage (highest first)
            profitable_routes.sort(key=lambda x: x['net_profit_percent'], reverse=True)
            
            # Create signals for top profitable routes
            for i, route in enumerate(profitable_routes[:3]):  # Top 3 most profitable routes
                signal = TradingSignal(
                    action='buy' if ai_signal.action == 'buy' else 'sell',
                    confidence=ai_signal.confidence,
                    price=route['buy_price'],
                    volume=ai_signal.volume,
                    timestamp=ai_signal.timestamp,
                    features=ai_signal.features,
                    model_used=ai_signal.model_used,
                    # Route information
                    buy_location=route['buy_system'],
                    sell_location=route['sell_system'],
                    profit_margin=route['profit_margin'],
                    transport_cost=route['transport_cost'],
                    net_profit_percent=route['net_profit_percent'],
                    opportunity_type=f"Cross-System Trade #{i+1}",
                    local_demand=route['target_opportunity'].local_demand,
                    local_supply=route['source_opportunity'].local_supply,
                    competition_level=route['source_opportunity'].competition_count,
                    action_plan=f"Buy {item_name} in {route['buy_system']} at {route['buy_price']:.2f} ISK, transport to {route['sell_system']}, sell at {route['sell_price']:.2f} ISK for {route['net_profit_percent']:.1f}% net profit"
                )
                
                signals.append(signal)
                
                logger.info(f"Profitable route #{i+1} for {item_name}: {route['buy_system']} → {route['sell_system']}")
                logger.info(f"  Buy: {route['buy_price']:.2f} ISK, Sell: {route['sell_price']:.2f} ISK")
                logger.info(f"  Net Profit: {route['net_profit_percent']:.1f}% (Transport: {route['transport_cost']:.0f} ISK)")
            
            if not profitable_routes:
                logger.info(f"No profitable cross-system routes found for {item_name}")
        
        except Exception as e:
            logger.error(f"Error finding profitable routes for {item_name}: {e}")
        
        return signals
    

    
    async def generate_system_based_signals(self, type_id: int, item_name: str) -> List[TradingSignal]:
        """Generate system-based trading signals using local market analysis."""
        signals = []
        
        try:
            # First, try to find the most profitable routes
            profitable_signals = await self.find_most_profitable_routes(type_id, item_name)
            signals.extend(profitable_signals)
            

        
        except Exception as e:
            logger.error(f"Error generating system-based signals for {item_name}: {e}")
        
        return signals
    
    def predict_trading_signals(self, df: pd.DataFrame, model_name: str = 'random_forest') -> List[TradingSignal]:
        """Generate trading signals using the best model."""
        if model_name not in self.models:
            logger.error(f"Model {model_name} not found. Available models: {list(self.models.keys())}")
            return []
        
        model = self.models[model_name]
        X = df[self.feature_columns].iloc[-1:].values
        
        if model_name == 'svm':
            X_scaled = self.scaler.transform(X)
            prediction = model.predict(X_scaled)[0]
            confidence = np.max(model.predict_proba(X_scaled)[0])
        else:
            prediction = model.predict(X)[0]
            confidence = np.max(model.predict_proba(X)[0])
        
        current_price = df['price'].iloc[-1]
        current_volume = df['volume_remain'].iloc[-1]
        current_time = df['issued'].iloc[-1]
        
        # Determine action based on prediction and confidence
        if prediction == 1 and confidence > 0.6:
            action = 'buy'
        elif prediction == 0 and confidence > 0.6:
            action = 'sell'
        else:
            action = 'hold'
        
        signal = TradingSignal(
            action=action,
            confidence=confidence,
            price=current_price,
            volume=current_volume,
            timestamp=current_time,
            features=dict(zip(self.feature_columns, X[0])),
            model_used=model_name
        )
        
        return [signal]
    
    def simulate_trading(self, type_id: int, days: int = 30) -> Dict[str, float]:
        """Simulate trading with the AI model."""
        logger.info(f"Starting trading simulation for type_id {type_id}")
        
        # Load data
        df = self.load_data(type_id, days)
        if df.empty:
            return {}
        
        # Engineer features
        df_feat = self.engineer_features(df)
        
        # Train models
        accuracies = self.train_models(df_feat)
        if not accuracies:
            return {}
        
        # Find best model
        best_model = max(accuracies, key=accuracies.get)
        logger.info(f"Best model: {best_model} with accuracy: {accuracies[best_model]:.3f}")
        
        # Simulate trading
        initial_value = self.portfolio_value
        trades_made = 0
        
        for i in range(len(df_feat) - 1):
            current_data = df_feat.iloc[:i+1]
            if len(current_data) < 50:  # Need enough data for prediction
                continue
            
            signals = self.predict_trading_signals(current_data, best_model)
            if not signals:
                continue
            
            signal = signals[0]
            
            # Execute trade based on signal
            if signal.action == 'buy' and signal.confidence > 0.7:
                # Buy with 10% of portfolio
                trade_amount = self.portfolio_value * 0.1
                quantity = int(trade_amount / signal.price)
                
                if quantity > 0:
                    self.portfolio_value -= quantity * signal.price
                    if type_id not in self.portfolio:
                        self.portfolio[type_id] = {'quantity': 0, 'avg_price': 0}
                    
                    # Update portfolio
                    total_quantity = self.portfolio[type_id]['quantity'] + quantity
                    total_cost = (self.portfolio[type_id]['quantity'] * self.portfolio[type_id]['avg_price']) + (quantity * signal.price)
                    self.portfolio[type_id]['quantity'] = total_quantity
                    self.portfolio[type_id]['avg_price'] = total_cost / total_quantity
                    
                    trades_made += 1
                    logger.info(f"BUY: {quantity} units at {signal.price:.2f} ISK (confidence: {signal.confidence:.3f})")
            
            elif signal.action == 'sell' and signal.confidence > 0.7:
                if type_id in self.portfolio and self.portfolio[type_id]['quantity'] > 0:
                    # Sell all holdings
                    quantity = self.portfolio[type_id]['quantity']
                    revenue = quantity * signal.price
                    self.portfolio_value += revenue
                    
                    # Calculate profit/loss
                    cost = quantity * self.portfolio[type_id]['avg_price']
                    profit = revenue - cost
                    
                    # Clear portfolio entry
                    self.portfolio[type_id] = {'quantity': 0, 'avg_price': 0}
                    
                    trades_made += 1
                    logger.info(f"SELL: {quantity} units at {signal.price:.2f} ISK (P&L: {profit:.2f} ISK)")
        
        # Calculate final portfolio value
        final_value = self.portfolio_value
        for type_id, holdings in self.portfolio.items():
            if holdings['quantity'] > 0:
                # Use last known price for valuation
                final_value += holdings['quantity'] * df_feat['price'].iloc[-1]
        
        total_return = ((final_value - initial_value) / initial_value) * 100
        
        results = {
            'initial_value': initial_value,
            'final_value': final_value,
            'total_return_pct': total_return,
            'trades_made': trades_made,
            'best_model': best_model,
            'model_accuracy': accuracies[best_model]
        }
        
        logger.info(f"Simulation complete. Total return: {total_return:.2f}%")
        return results
    
    def plot_trading_results(self, df: pd.DataFrame, signals: List[TradingSignal]):
        """Plot trading signals and price movements."""
        plt.figure(figsize=(15, 8))
        
        # Plot price
        plt.subplot(2, 1, 1)
        plt.plot(df['issued'], df['price'], label='Price', alpha=0.7)
        
        # Plot moving averages
        plt.plot(df['issued'], df['price_ma7'], label='7-day MA', alpha=0.6)
        plt.plot(df['issued'], df['price_ma21'], label='21-day MA', alpha=0.6)
        
        # Plot signals
        for signal in signals:
            if signal.action == 'buy':
                plt.scatter(signal.timestamp, signal.price, marker='^', color='green', s=100, label='Buy Signal' if signal == signals[0] else "")
            elif signal.action == 'sell':
                plt.scatter(signal.timestamp, signal.price, marker='v', color='red', s=100, label='Sell Signal' if signal == signals[0] else "")
        
        plt.title('AI Trading Signals')
        plt.xlabel('Date')
        plt.ylabel('Price (ISK)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Plot confidence scores
        plt.subplot(2, 1, 2)
        confidences = [signal.confidence for signal in signals]
        timestamps = [signal.timestamp for signal in signals]
        plt.scatter(timestamps, confidences, c=['green' if s.action == 'buy' else 'red' if s.action == 'sell' else 'blue' for s in signals])
        plt.title('Signal Confidence Scores')
        plt.xlabel('Date')
        plt.ylabel('Confidence')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def main():
    """Main function to run the advanced AI trader."""
    trader = AdvancedAITrader()
    
    # Test with Tritanium (type_id 34)
    type_id = 34
    item_name = "Tritanium"
    
    logger.info(f"Starting advanced AI trading analysis for {item_name}")
    
    # Set target system for system-based trading
    trader.set_target_system("Jita")
    
    # Generate system-based signals
    system_signals = asyncio.run(trader.generate_system_based_signals(type_id, item_name))
    
    if system_signals:
        print("\n" + "="*50)
        print("SYSTEM-BASED TRADING SIGNALS")
        print("="*50)
        print(f"Item: {item_name}")
        for signal in system_signals:
            print(f"Action: {signal.action}, Confidence: {signal.confidence:.1%}, Price: {signal.price:.2f} ISK")
            if signal.buy_location:
                print(f"Buy Location: {signal.buy_location}")
            if signal.sell_location:
                print(f"Sell Location: {signal.sell_location}")
            if signal.profit_margin:
                print(f"Profit Margin: {signal.profit_margin:.2%}, Net Profit: {signal.net_profit_percent:.2f}%")
            if signal.opportunity_type:
                print(f"Opportunity Type: {signal.opportunity_type}")
            if signal.action_plan:
                print(f"Action Plan: {signal.action_plan}")
            print("-"*20)
        print("="*50)
    
    # Run trading simulation
    results = trader.simulate_trading(type_id, days=90)
    
    if results:
        print("\n" + "="*50)
        print("AI TRADING SIMULATION RESULTS")
        print("="*50)
        print(f"Item: {item_name}")
        print(f"Initial Portfolio Value: {results['initial_value']:,.0f} ISK")
        print(f"Final Portfolio Value: {results['final_value']:,.0f} ISK")
        print(f"Total Return: {results['total_return_pct']:.2f}%")
        print(f"Trades Made: {results['trades_made']}")
        print(f"Best Model: {results['best_model']}")
        print(f"Model Accuracy: {results['model_accuracy']:.3f}")
        print("="*50)
    
    # Load data for visualization
    df = trader.load_data(type_id, days=90)
    if not df.empty:
        df_feat = trader.engineer_features(df)
        trader.train_models(df_feat)
        
        # Generate signals for visualization
        signals = []
        for i in range(50, len(df_feat)):
            current_data = df_feat.iloc[:i+1]
            current_signals = trader.predict_trading_signals(current_data, results.get('best_model', 'random_forest'))
            signals.extend(current_signals)
        
        # Plot results
        trader.plot_trading_results(df_feat, signals)

if __name__ == "__main__":
    main() 
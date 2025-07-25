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
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def train_models(self, df: pd.DataFrame) -> Dict[str, float]:
        """Train multiple ML models and return their accuracies."""
        if df.empty or len(df) < 50:
            logger.error("Not enough data to train models.")
            return {}
        
        X = df[self.feature_columns]
        y = df['target']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Define models
        models = {
            'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
            'random_forest': RandomForestClassifier(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
            'svm': SVC(kernel='rbf', probability=True, random_state=42)
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
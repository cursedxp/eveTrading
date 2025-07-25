#!/usr/bin/env python3
"""
EVE Trading System Frontend
Modern web interface with EVE SSO integration
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_socketio import SocketIO, emit
import requests
import json
import os
from datetime import datetime, timedelta
import asyncio
import threading
import time
from typing import Dict, List, Optional
import logging

# Import our trading system components
import sys
sys.path.append('..')
from ai_trader import AdvancedAITrader
from portfolio_manager import PortfolioManager
from database_simple import SimpleDatabaseManager
from automated_monitor import AutomatedMarketMonitor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
socketio = SocketIO(app, cors_allowed_origins="*")

# EVE SSO Configuration
EVE_CLIENT_ID = os.environ.get('EVE_CLIENT_ID', 'your-eve-client-id')
EVE_CLIENT_SECRET = os.environ.get('EVE_CLIENT_SECRET', 'your-eve-client-secret')
EVE_CALLBACK_URL = 'http://localhost:5000/callback'

# Trading system components
ai_trader = None
portfolio_manager = None
market_monitor = None
db_manager = None

# Real-time data storage
market_data = {}
trading_signals = []
portfolio_data = {}
character_info = {}

class EVETradingFrontend:
    """Frontend controller for EVE Trading System"""
    
    def __init__(self):
        self.ai_trader = AdvancedAITrader()
        self.portfolio_manager = PortfolioManager()
        self.market_monitor = AutomatedMarketMonitor()
        self.db_manager = SimpleDatabaseManager()
        self.character_info = {}
        self.is_monitoring = False
        
    def get_character_info(self, access_token: str) -> Dict:
        """Get character information from EVE SSO"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            # Get character info
            response = requests.get(
                'https://esi.evetech.net/latest/characters/me/',
                headers=headers
            )
            
            if response.status_code == 200:
                character_data = response.json()
                
                # Get character wallet
                wallet_response = requests.get(
                    f'https://esi.evetech.net/latest/characters/{character_data["character_id"]}/wallet/',
                    headers=headers
                )
                
                wallet_balance = 0
                if wallet_response.status_code == 200:
                    wallet_balance = wallet_response.json()
                
                return {
                    'character_id': character_data['character_id'],
                    'name': character_data['name'],
                    'corporation_id': character_data.get('corporation_id'),
                    'alliance_id': character_data.get('alliance_id'),
                    'wallet_balance': wallet_balance,
                    'last_login': character_data.get('last_login'),
                    'security_status': character_data.get('security_status', 0)
                }
            
        except Exception as e:
            logger.error(f"Error getting character info: {e}")
        
        return {}
    
    def get_character_assets(self, access_token: str, character_id: int) -> List[Dict]:
        """Get character assets from EVE API"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'https://esi.evetech.net/latest/characters/{character_id}/assets/',
                headers=headers
            )
            
            if response.status_code == 200:
                assets = response.json()
                
                # Get item names
                item_ids = list(set([asset['type_id'] for asset in assets]))
                names_response = requests.post(
                    'https://esi.evetech.net/latest/universe/names/',
                    json=item_ids
                )
                
                item_names = {}
                if names_response.status_code == 200:
                    names_data = names_response.json()
                    item_names = {item['id']: item['name'] for item in names_data}
                
                # Format assets
                formatted_assets = []
                for asset in assets:
                    formatted_assets.append({
                        'type_id': asset['type_id'],
                        'name': item_names.get(asset['type_id'], f"Unknown Item {asset['type_id']}"),
                        'quantity': asset['quantity'],
                        'location_id': asset['location_id'],
                        'location_flag': asset.get('location_flag', ''),
                        'is_singleton': asset.get('is_singleton', False)
                    })
                
                return formatted_assets
            
        except Exception as e:
            logger.error(f"Error getting character assets: {e}")
        
        return []
    
    def get_market_orders(self, access_token: str, character_id: int) -> List[Dict]:
        """Get character's market orders"""
        try:
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'https://esi.evetech.net/latest/characters/{character_id}/orders/',
                headers=headers
            )
            
            if response.status_code == 200:
                orders = response.json()
                return orders
            
        except Exception as e:
            logger.error(f"Error getting market orders: {e}")
        
        return []
    
    def start_monitoring(self, character_id: int, access_token: str):
        """Start real-time monitoring for the character"""
        global is_monitoring
        is_monitoring = True
        
        def monitor_loop():
            while is_monitoring:
                try:
                    # Get real-time data
                    character_info = self.get_character_info(access_token)
                    assets = self.get_character_assets(access_token, character_id)
                    orders = self.get_market_orders(access_token, character_id)
                    
                    # Run AI analysis
                    ai_signals = self.ai_trader.predict_trading_signals(
                        self.ai_trader.load_data(34, days=7)
                    )
                    
                    # Emit data to frontend
                    socketio.emit('market_update', {
                        'character_info': character_info,
                        'assets': assets,
                        'orders': orders,
                        'ai_signals': [signal.__dict__ for signal in ai_signals],
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    time.sleep(30)  # Update every 30 seconds
                    
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(60)
        
        # Start monitoring in background thread
        thread = threading.Thread(target=monitor_loop)
        thread.daemon = True
        thread.start()

# Initialize frontend controller
frontend_controller = EVETradingFrontend()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/login')
def login():
    """Redirect to EVE SSO login"""
    eve_sso_url = (
        f"https://login.eveonline.com/v2/oauth/authorize?"
        f"response_type=code&"
        f"redirect_uri={EVE_CALLBACK_URL}&"
        f"client_id={EVE_CLIENT_ID}&"
        f"scope=publicData esi-wallet.read_character_wallet.v1 "
        f"esi-assets.read_assets.v1 esi-markets.structure_markets.v1 "
        f"esi-universe.read_structures.v1"
    )
    return redirect(eve_sso_url)

@app.route('/callback')
def callback():
    """Handle EVE SSO callback"""
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('index'))
    
    try:
        # Exchange code for access token
        token_response = requests.post(
            'https://login.eveonline.com/v2/oauth/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': EVE_CLIENT_ID,
                'client_secret': EVE_CLIENT_SECRET
            },
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        if token_response.status_code == 200:
            token_data = token_response.json()
            access_token = token_data['access_token']
            
            # Get character info
            character_info = frontend_controller.get_character_info(access_token)
            
            # Store in session
            session['access_token'] = access_token
            session['character_info'] = character_info
            
            # Start monitoring
            frontend_controller.start_monitoring(
                character_info['character_id'],
                access_token
            )
            
            return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error in callback: {e}")
    
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    """Trading dashboard"""
    if 'character_info' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', character=session['character_info'])

@app.route('/api/character')
def api_character():
    """API endpoint for character data"""
    if 'character_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    return jsonify(session['character_info'])

@app.route('/api/assets')
def api_assets():
    """API endpoint for character assets"""
    if 'access_token' not in session or 'character_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    assets = frontend_controller.get_character_assets(
        session['access_token'],
        session['character_info']['character_id']
    )
    
    return jsonify(assets)

@app.route('/api/orders')
def api_orders():
    """API endpoint for market orders"""
    if 'access_token' not in session or 'character_info' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    orders = frontend_controller.get_market_orders(
        session['access_token'],
        session['character_info']['character_id']
    )
    
    return jsonify(orders)

@app.route('/api/trading-signals')
def api_trading_signals():
    """API endpoint for AI trading signals"""
    try:
        # Load data and generate signals
        df = frontend_controller.ai_trader.load_data(34, days=7)
        if not df.empty:
            df = frontend_controller.ai_trader.engineer_features(df)
            frontend_controller.ai_trader.train_models(df)
            signals = frontend_controller.ai_trader.predict_trading_signals(df)
            
            return jsonify([signal.__dict__ for signal in signals])
    except Exception as e:
        logger.error(f"Error generating trading signals: {e}")
    
    return jsonify([])

@app.route('/api/portfolio')
def api_portfolio():
    """API endpoint for portfolio data"""
    try:
        portfolio_summary = frontend_controller.portfolio_manager.get_portfolio_summary()
        portfolio_items = frontend_controller.portfolio_manager.get_portfolio_items()
        performance_metrics = frontend_controller.portfolio_manager.get_performance_metrics()
        
        return jsonify({
            'summary': portfolio_summary,
            'items': portfolio_items,
            'performance': performance_metrics
        })
    except Exception as e:
        logger.error(f"Error getting portfolio data: {e}")
        return jsonify({})

@socketio.on('connect')
def handle_connect():
    """Handle WebSocket connection"""
    emit('connected', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    logger.info('Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """Start real-time monitoring"""
    if 'access_token' in session and 'character_info' in session:
        frontend_controller.start_monitoring(
            session['character_info']['character_id'],
            session['access_token']
        )
        emit('monitoring_started', {'status': 'started'})

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 
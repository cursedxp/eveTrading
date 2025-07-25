#!/usr/bin/env python3
"""
Simple web dashboard for EVE Market Data visualization.
This provides a web interface to view the generated charts and market data.
"""

from flask import Flask, render_template_string, send_from_directory
import os
import glob
from datetime import datetime
import json

app = Flask(__name__)

# HTML template for the dashboard
DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EVE Market Analysis Dashboard</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.1em;
        }
        .content {
            padding: 30px;
        }
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }
        .chart-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .chart-card:hover {
            transform: translateY(-5px);
        }
        .chart-card h3 {
            margin: 0 0 15px 0;
            color: #2c3e50;
            font-size: 1.3em;
        }
        .chart-image {
            width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-card h4 {
            margin: 0 0 10px 0;
            font-size: 0.9em;
            opacity: 0.9;
        }
        .stat-card .value {
            font-size: 1.8em;
            font-weight: bold;
        }
        .refresh-btn {
            background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 25px;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.3s ease;
        }
        .refresh-btn:hover {
            transform: scale(1.05);
        }
        .last-updated {
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 EVE Market Analysis Dashboard</h1>
            <p>Real-time market data visualization and analysis</p>
        </div>
        
        <div class="content">
            <div style="text-align: center; margin-bottom: 30px;">
                <button class="refresh-btn" onclick="location.reload()">
                    🔄 Refresh Data
                </button>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <h4>Total Orders</h4>
                    <div class="value">{{ stats.total_orders }}</div>
                </div>
                <div class="stat-card">
                    <h4>Average Price</h4>
                    <div class="value">{{ "%.2f"|format(stats.avg_price) }} ISK</div>
                </div>
                <div class="stat-card">
                    <h4>Total Volume</h4>
                    <div class="value">{{ "{:,}".format(stats.total_volume) }}</div>
                </div>
                <div class="stat-card">
                    <h4>Unique Locations</h4>
                    <div class="value">{{ stats.unique_locations }}</div>
                </div>
            </div>
            
            <div class="chart-grid">
                {% for chart in charts %}
                <div class="chart-card">
                    <h3>{{ chart.title }}</h3>
                    <img src="{{ chart.url }}" alt="{{ chart.title }}" class="chart-image">
                </div>
                {% endfor %}
            </div>
            
            <div class="last-updated">
                Last updated: {{ last_updated }}
            </div>
        </div>
    </div>
</body>
</html>
"""

def get_chart_files():
    """Get all chart files from the charts directory."""
    charts_dir = "charts"
    if not os.path.exists(charts_dir):
        return []
    
    chart_files = glob.glob(os.path.join(charts_dir, "*.png"))
    charts = []
    
    for file_path in chart_files:
        filename = os.path.basename(file_path)
        chart_type = filename.split('_')[0].replace('_', ' ').title()
        charts.append({
            'title': chart_type,
            'url': f'/charts/{filename}',
            'filename': filename
        })
    
    return sorted(charts, key=lambda x: x['title'])

def get_market_stats():
    """Get basic market statistics (mock data for now)."""
    return {
        'total_orders': 223,
        'avg_price': 6101.53,
        'total_volume': 30487650650,
        'unique_locations': 65
    }

@app.route('/')
def dashboard():
    """Main dashboard page."""
    charts = get_chart_files()
    stats = get_market_stats()
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return render_template_string(
        DASHBOARD_TEMPLATE,
        charts=charts,
        stats=stats,
        last_updated=last_updated
    )

@app.route('/charts/<filename>')
def serve_chart(filename):
    """Serve chart images."""
    return send_from_directory('charts', filename)

@app.route('/api/charts')
def api_charts():
    """API endpoint to get chart information."""
    charts = get_chart_files()
    return {'charts': charts}

if __name__ == '__main__':
    print("🌐 Starting EVE Market Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    print("📈 Charts directory: charts/")
    print("🔄 Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 
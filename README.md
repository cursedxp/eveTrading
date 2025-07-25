# 🚀 EVE Trading Market Analysis Tool

A comprehensive Python-based tool for analyzing EVE Online market data with real-time data fetching, advanced visualizations, and a beautiful web dashboard.

## ✨ Features

### 🔄 **Async Data Fetching**

- **Concurrent API calls** using `aiohttp` for efficient data retrieval
- **Rate limiting** and error handling for robust API interactions
- **Multiple item support** with parallel processing

### 📊 **Advanced Data Visualization**

- **Price Distribution Analysis** with histograms and box plots
- **Volume vs Price Scatter Plots** with trend analysis
- **Market Depth Analysis** showing cumulative volume curves
- **Location-based Analysis** for trading hub insights
- **Comprehensive Dashboard** with multiple chart types

### 🌐 **Web Dashboard**

- **Beautiful responsive interface** with modern CSS styling
- **Real-time chart display** with interactive elements
- **Statistics overview** with key market metrics
- **Mobile-friendly design** for on-the-go analysis

### 🛠 **Technical Excellence**

- **Type hints** throughout for better code maintainability
- **Comprehensive error handling** and logging
- **Modular architecture** for easy extension
- **Environment-based configuration** for flexibility

## 📋 Requirements

- Python 3.13+
- Virtual environment (recommended)
- EVE Online ESI API access

## 🚀 Quick Start

### 1. **Environment Setup**

```bash
# Clone the repository
git clone <your-repo-url>
cd eveTrading

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. **Configuration**

Create a `.env` file in the project root:

```env
BASE_URL=https://esi.evetech.net/latest
```

### 3. **Run the Application**

#### **Data Fetching & Analysis**

```bash
python run.py
```

#### **Web Dashboard**

```bash
python web_dashboard.py
```

Then visit: http://localhost:5000

## 📁 Project Structure

```
eveTrading/
├── fetchMarketData.py      # Main data fetching and analysis
├── market_visualizer.py    # Data visualization module
├── web_dashboard.py        # Web interface
├── run.py                  # Runner script
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── charts/                 # Generated charts
└── README.md              # This file
```

## 🎯 Core Components

### **1. Data Fetching (`fetchMarketData.py`)**

- **Async HTTP requests** with `aiohttp`
- **Concurrent processing** for multiple items
- **Error handling** and timeout management
- **Data analysis** with pandas

### **2. Visualization (`market_visualizer.py`)**

- **Price Distribution Charts** with statistical overlays
- **Volume Analysis** with scatter plots and trend lines
- **Market Depth Curves** for liquidity analysis
- **Location-based Insights** for trading hub analysis
- **Comprehensive Dashboards** with multiple visualizations

### **3. Web Interface (`web_dashboard.py`)**

- **Flask-based web server**
- **Responsive HTML/CSS** design
- **Real-time chart serving**
- **Statistics display**

## 📊 Chart Types Generated

1. **Price Distribution** - Histogram with mean/median lines
2. **Volume vs Price Scatter** - With trend analysis
3. **Market Depth** - Cumulative volume curves
4. **Location Analysis** - Trading hub insights
5. **Comprehensive Dashboard** - Multi-panel overview

## 🔧 Advanced Usage

### **Custom Item Analysis**

```python
# Modify fetchMarketData.py
type_id = 35  # Change to different item ID
item_name = "Pyerite"  # Update item name
```

### **Multiple Items Concurrently**

```python
# Uncomment in fetchMarketData.py
type_ids = [34, 35, 36]  # Tritanium, Pyerite, Mexallon
concurrent_data = await fetch_multiple_market_orders(type_ids)
```

### **Custom Visualizations**

```python
from market_visualizer import MarketVisualizer

visualizer = MarketVisualizer()
# Generate specific charts
visualizer.create_price_distribution(df, "Custom Item")
visualizer.create_volume_price_scatter(df, "Custom Item")
```

## 🎓 Learning Progress

### **✅ Completed Skills**

- **Async Programming** - Efficient concurrent API calls
- **Data Visualization** - Matplotlib and Seaborn mastery
- **Web Development** - Flask web applications
- **Type Hints** - Modern Python practices
- **Error Handling** - Robust application design
- **Modular Architecture** - Clean, maintainable code

### **🚀 Next Phase Opportunities**

- **Database Integration** - Store historical data
- **Real-time Updates** - WebSocket connections
- **Advanced Analytics** - Machine learning insights
- **Mobile App** - React Native or Flutter
- **Trading Bots** - Automated market analysis

## 🛠 Technical Stack

| Component           | Technology               | Purpose            |
| ------------------- | ------------------------ | ------------------ |
| **HTTP Client**     | `aiohttp`                | Async API requests |
| **Data Processing** | `pandas`                 | Data manipulation  |
| **Visualization**   | `matplotlib` + `seaborn` | Chart generation   |
| **Web Framework**   | `Flask`                  | Web dashboard      |
| **Environment**     | `python-dotenv`          | Configuration      |
| **Type System**     | `typing`                 | Code safety        |

## 📈 Performance Features

- **Concurrent API calls** for faster data retrieval
- **Efficient memory usage** with streaming data processing
- **Optimized chart generation** with high DPI output
- **Responsive web interface** for all devices

## 🔒 Security & Best Practices

- **Environment variables** for sensitive configuration
- **Error handling** throughout the application
- **Input validation** for API parameters
- **Logging** for debugging and monitoring
- **Type hints** for code safety

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is for educational purposes. Please respect EVE Online's API terms of service.

## 🎯 Future Enhancements

- **Real-time data streaming**
- **Machine learning price predictions**
- **Advanced trading algorithms**
- **Mobile application**
- **Database integration**
- **API rate limiting optimization**

---

**Built with ❤️ for EVE Online market analysis**

_Your journey from basic data fetching to comprehensive market analysis is complete! 🚀_

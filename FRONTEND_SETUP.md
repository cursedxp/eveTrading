# 🎮 EVE Trading System - Next.js Frontend Setup

A modern, game-ready frontend for your EVE Trading System that you can use while playing EVE Online.

## 🚀 Quick Start

### Option 1: Automatic Setup (Recommended)

```bash
# Start both backend and frontend automatically
python start_frontend.py
```

### Option 2: Manual Setup

```bash
# 1. Install frontend dependencies
cd frontend
npm install

# 2. Start the frontend (in one terminal)
npm run dev

# 3. Start the backend (in another terminal)
python web_dashboard.py
```

## 📋 Prerequisites

- **Node.js 18+** - [Download here](https://nodejs.org/)
- **Python 3.8+** - Already installed
- **npm or yarn** - Comes with Node.js

## 🎯 Features

### 🎮 Game-Ready Interface

- **Dark EVE-themed design** - Easy on the eyes during long gaming sessions
- **Responsive layout** - Works on desktop and mobile
- **Real-time updates** - Live market data and trading signals
- **Minimal resource usage** - Won't impact game performance

### 📊 Dashboard Components

1. **Stats Cards** - Portfolio value, active signals, market items, AI accuracy
2. **Market Overview** - Real-time market data with price changes
3. **Trading Signals** - AI-generated buy/sell recommendations
4. **Portfolio** - Current holdings and P&L tracking

### 🔄 Real-time Features

- **Live market data** - Updates every 30 seconds
- **AI trading signals** - Instant notifications
- **Connection status** - Shows backend connectivity
- **Auto-refresh** - Keeps data current

## 🎨 Design Features

### EVE Online Theme

- **Dark color scheme** - `#1a1a2e` primary, `#16213e` secondary
- **EVE-inspired colors** - Red accent `#e94560` for highlights
- **Orbitron font** - Futuristic typeface for headers
- **Smooth animations** - Framer Motion for transitions

### Responsive Design

- **Desktop optimized** - Full dashboard layout
- **Mobile friendly** - Collapsible sidebar
- **Game overlay ready** - Can be used as overlay window

## 🔧 Technical Stack

### Frontend

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Modern icons
- **Axios** - HTTP client for API calls

### Backend Integration

- **REST API** - Connects to Python backend
- **WebSocket** - Real-time data updates
- **EVE ESI API** - Game data integration

## 📁 Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles with EVE theme
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main dashboard
│   └── components/        # Reusable components
│       └── DataFetcher.tsx # API integration
├── public/                # Static assets
├── package.json           # Dependencies
├── tailwind.config.js     # EVE theme configuration
└── README.md             # Frontend documentation
```

## 🎮 Usage While Gaming

### Window Management

1. **Open in browser** - Navigate to `http://localhost:3000`
2. **Resize window** - Make it small enough to fit alongside EVE
3. **Position strategically** - Place on second monitor or corner of main screen
4. **Keep visible** - Monitor trading signals and market changes

### Key Features for Gaming

- **Connection status** - Shows if backend is running
- **Real-time alerts** - New trading signals appear instantly
- **Quick refresh** - Manual refresh button
- **Minimal UI** - Clean, distraction-free design

## 🔄 Data Flow

```
EVE ESI API → Python Backend → Next.js Frontend
     ↓              ↓              ↓
Market Data → AI Analysis → Real-time Dashboard
```

### Real-time Updates

- **Market data** - Fetched every 30 seconds
- **Trading signals** - AI-generated recommendations
- **Portfolio** - Current holdings and P&L
- **Connection** - Backend health monitoring

## 🛠️ Development

### Adding New Features

1. **Create component** - Add to `app/components/`
2. **Update API** - Add endpoint to Python backend
3. **Connect frontend** - Use `DataFetcher.tsx` pattern
4. **Style with Tailwind** - Use `eve-` prefixed classes

### Customization

- **Colors** - Edit `tailwind.config.js` for theme changes
- **Layout** - Modify `app/page.tsx` for dashboard layout
- **API endpoints** - Update `DataFetcher.tsx` for new data sources

## 🚀 Deployment

### Local Development

```bash
# Development mode with hot reload
npm run dev
```

### Production Build

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Vercel Deployment

```bash
# Deploy to Vercel
npm install -g vercel
vercel
```

## 🔧 Troubleshooting

### Common Issues

**Frontend won't start:**

```bash
# Check Node.js version
node --version  # Should be 18+

# Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Backend connection failed:**

```bash
# Check if Python backend is running
python web_dashboard.py

# Check port 5000 is available
lsof -i :5000
```

**API errors:**

- Ensure Python backend is running on `localhost:5000`
- Check CORS settings in `web_dashboard.py`
- Verify API endpoints in `DataFetcher.tsx`

### Performance Tips

- **Close unused tabs** - Reduces memory usage
- **Use hardware acceleration** - Enable in browser settings
- **Monitor resource usage** - Check Task Manager
- **Position window carefully** - Avoid overlapping with game UI

## 🎯 Next Steps

### Planned Features

- **EVE SSO integration** - Character authentication
- **Real-time charts** - Price history visualization
- **Alert system** - Custom price alerts
- **Mobile app** - React Native version
- **Desktop app** - Electron wrapper

### Customization Ideas

- **Custom themes** - Different color schemes
- **Layout options** - Configurable dashboard
- **Widget system** - Draggable components
- **Plugin system** - Third-party extensions

## 📞 Support

### Getting Help

1. **Check logs** - Browser console and terminal output
2. **Verify setup** - Run `python start_frontend.py` for automatic checks
3. **Test components** - Use browser dev tools
4. **Check documentation** - See `README.md` files

### Contributing

1. **Fork repository** - Create your own copy
2. **Make changes** - Add features or fix bugs
3. **Test thoroughly** - Ensure everything works
4. **Submit pull request** - Share your improvements

---

**🎮 Happy Trading!** Your EVE Trading System now has a modern, game-ready frontend that you can use while playing EVE Online!

# EVE Trading System - Frontend

A modern Next.js frontend for the EVE Trading System, designed to be used while playing EVE Online.

## Features

- 🎮 **Game-Ready Interface**: Optimized for use while playing EVE Online
- 📊 **Real-time Dashboard**: Live market data and trading signals
- 🎨 **EVE-themed Design**: Dark theme with EVE Online aesthetics
- 📱 **Responsive Design**: Works on desktop and mobile
- ⚡ **Fast Performance**: Built with Next.js 14 and TypeScript
- 🔄 **Real-time Updates**: WebSocket integration for live data

## Tech Stack

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Lucide React**: Modern icons
- **Recharts**: Data visualization
- **Socket.IO**: Real-time communication
- **Framer Motion**: Smooth animations

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Python backend running on localhost:5000

### Installation

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install
   ```

2. **Start the development server:**

   ```bash
   npm run dev
   ```

3. **Open your browser:**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Development

- **Hot Reload**: Changes appear instantly
- **TypeScript**: Full type safety
- **ESLint**: Code quality checks
- **Tailwind**: Utility-first CSS

### Building for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Dashboard page
├── components/             # Reusable components
├── lib/                   # Utilities and helpers
├── public/                # Static assets
└── package.json           # Dependencies
```

## Features

### Dashboard Components

1. **Stats Cards**: Portfolio value, signals, items, AI accuracy
2. **Market Overview**: Real-time market data table
3. **Trading Signals**: AI-generated buy/sell recommendations
4. **Portfolio**: Current holdings and P&L

### Real-time Features

- Live market data updates
- AI trading signal notifications
- Portfolio value tracking
- Connection status monitoring

### EVE Integration

- EVE SSO authentication
- Character data display
- Market order integration
- Asset tracking

## Customization

### Colors

The theme uses EVE Online-inspired colors:

- Primary: `#1a1a2e` (Dark blue)
- Secondary: `#16213e` (Medium blue)
- Accent: `#0f3460` (Light blue)
- Highlight: `#e94560` (Red accent)

### Components

All components use the `eve-` prefix for consistent styling:

- `.eve-card`: Card containers
- `.eve-button`: Action buttons
- `.eve-table`: Data tables
- `.eve-input`: Form inputs

## API Integration

The frontend connects to the Python backend via:

- REST API endpoints
- WebSocket for real-time updates
- EVE ESI API for game data

## Performance

- **Lazy Loading**: Components load on demand
- **Image Optimization**: Next.js automatic optimization
- **Code Splitting**: Automatic bundle splitting
- **Caching**: Built-in caching strategies

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

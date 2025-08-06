#!/bin/bash

# EVE Trading System - Unified Runner Script
# Supports the streamlined Profitable Routes system

echo "🚀 EVE Trading System - Profitable Routes"
echo "=========================================="

# Function definitions
show_help() {
    echo "Usage: ./run_all.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  all          - Run data analysis and start frontend (default)"
    echo "  frontend     - Start only the Next.js frontend"
    echo "  data         - Run only the data analysis"
    echo "  setup        - Install dependencies and setup environment"
    echo "  clean        - Clean build artifacts and logs"
    echo "  test         - Test the system"
    echo "  status       - Check if frontend is running"
    echo "  help         - Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./run_all.sh all        # Full system startup"
    echo "  ./run_all.sh frontend   # Just start the UI"
    echo "  ./run_all.sh data       # Just update data"
    echo "  ./run_all.sh status     # Check if system is running"
}

setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Check Python environment
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    echo "🐍 Activating Python virtual environment..."
    source venv/bin/activate
    
    # Install Python dependencies
    echo "📚 Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install Node.js dependencies
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
    
    echo "✅ Environment setup complete!"
}

run_data_analysis() {
    echo "📊 Running profitable routes analysis..."
    
    # Activate Python environment
    source venv/bin/activate
    
    # Run the profitable routes finder
    echo "🔍 Starting data analysis (this may take a few minutes)..."
    python profitable_route_finder_final.py
    
    if [ $? -eq 0 ]; then
        echo "✅ Data analysis completed successfully!"
        return 0
    else
        echo "❌ Data analysis failed!"
        return 1
    fi
}

start_frontend() {
    echo "🌐 Starting Next.js frontend..."
    
    # Check if we're in the right directory
    if [ ! -d "frontend" ]; then
        echo "❌ Frontend directory not found. Make sure you're in the EVE Trading root directory."
        return 1
    fi
    
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing Node.js dependencies..."
        npm install
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install Node.js dependencies"
            return 1
        fi
    fi
    
    # Start the development server
    echo ""
    echo "🎯 Frontend will be available at: http://localhost:3000"
    echo "📡 API endpoints:"
    echo "   • Health: http://localhost:3000/api/health"
    echo "   • Profitable Routes: http://localhost:3000/api/profitable-routes"
    echo ""
    echo "🚨 IMPORTANT: The development server will keep running."
    echo "   Press Ctrl+C to stop the server when you're done."
    echo "   The terminal will show live reload messages as you make changes."
    echo ""
    echo "⏳ Starting development server..."
    
    npm run dev
    
    # This will only execute if npm run dev exits (which happens when user presses Ctrl+C)
    echo ""
    echo "🛑 Frontend development server stopped."
}

test_system() {
    echo "🧪 Testing system components..."
    
    # Test MongoDB connection
    echo "📡 Testing MongoDB connection..."
    source venv/bin/activate
    python -c "
from mongodb_service import get_mongodb_service
try:
    mongo = get_mongodb_service()
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
"
    
    # Test frontend build
    echo "🏗️ Testing frontend build..."
    cd frontend
    npm run build
    if [ $? -eq 0 ]; then
        echo "✅ Frontend build successful!"
    else
        echo "❌ Frontend build failed!"
        return 1
    fi
    cd ..
    
    echo "✅ System tests completed!"
}

clean_system() {
    echo "🧹 Cleaning build artifacts and logs..."
    
    # Clean frontend build
    cd frontend
    rm -rf .next
    rm -rf node_modules/.cache
    echo "✅ Frontend artifacts cleaned"
    cd ..
    
    # Clean Python cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    find . -name "*.pyc" -delete 2>/dev/null
    echo "✅ Python cache cleaned"
    
    # Clean log files
    rm -f *.log
    echo "✅ Log files cleaned"
    
    echo "🎉 Cleanup completed!"
}

check_status() {
    echo "🔍 Checking system status..."
    
    # Check if Next.js is running
    if pgrep -f "next dev" > /dev/null 2>&1; then
        echo "✅ Next.js development server is RUNNING"
        
        # Try to reach the health endpoint
        if command -v curl >/dev/null 2>&1; then
            echo "🏥 Testing health endpoint..."
            if curl -s -f http://localhost:3000/api/health > /dev/null 2>&1; then
                echo "✅ Frontend API is RESPONDING"
                echo "🌐 Frontend available at: http://localhost:3000"
            else
                echo "⚠️  Frontend API not responding (may still be starting up)"
            fi
        else
            echo "ℹ️  Cannot test API (curl not available)"
        fi
    else
        echo "❌ Next.js development server is NOT running"
        echo "💡 Start it with: ./run_all.sh frontend"
    fi
    
    # Check Python processes
    if pgrep -f "profitable_route_finder_final.py" > /dev/null 2>&1; then
        echo "✅ Data analysis script is RUNNING"
    else
        echo "ℹ️  Data analysis script is not currently running"
    fi
    
    # Check if MongoDB is accessible
    echo "📊 Checking data availability..."
    source venv/bin/activate 2>/dev/null
    python -c "
try:
    from mongodb_service import get_mongodb_service
    mongo = get_mongodb_service()
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'⚠️  MongoDB connection issue: {e}')
" 2>/dev/null
}

run_all() {
    echo "🚀 Starting full EVE Trading system..."
    
    # First, run data analysis
    echo "📊 Step 1: Data Analysis"
    if run_data_analysis; then
        echo ""
        echo "🌐 Step 2: Starting Frontend"
        echo "   The frontend will automatically use the fresh data"
        echo "   Press Ctrl+C to stop the frontend when done"
        echo ""
        start_frontend
    else
        echo "❌ Failed to run data analysis. Frontend may still work with existing data."
        echo "🤔 Would you like to start the frontend anyway? (y/N)"
        read -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            start_frontend
        fi
    fi
}

# Main script logic
case "${1:-all}" in
    "all")
        run_all
        ;;
    "frontend")
        start_frontend
        ;;
    "data")
        run_data_analysis
        ;;
    "setup")
        setup_environment
        ;;
    "clean")
        clean_system
        ;;
    "test")
        test_system
        ;;
    "status")
        check_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
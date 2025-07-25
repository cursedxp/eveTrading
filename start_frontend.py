#!/usr/bin/env python3
"""
Startup script for EVE Trading System Frontend
Runs both the Python backend and Next.js frontend
"""

import subprocess
import sys
import os
import time
import signal
import threading
from pathlib import Path

class FrontendManager:
    def __init__(self):
        self.backend_process = None
        self.frontend_process = None
        self.running = True
        
    def start_backend(self):
        """Start the Python backend server"""
        print("🚀 Starting Python backend server...")
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "web_dashboard.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Backend server started on http://localhost:5000")
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
        return True
    
    def start_frontend(self):
        """Start the Next.js frontend server"""
        print("🎮 Starting Next.js frontend server...")
        frontend_dir = Path("frontend")
        
        if not frontend_dir.exists():
            print("❌ Frontend directory not found. Please run 'npm install' in the frontend directory first.")
            return False
            
        try:
            # Change to frontend directory
            os.chdir(frontend_dir)
            
            # Start Next.js development server
            self.frontend_process = subprocess.Popen([
                "npm", "run", "dev"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Change back to root directory
            os.chdir("..")
            
            print("✅ Frontend server started on http://localhost:3000")
            return True
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def stop_servers(self):
        """Stop both servers"""
        print("\n🛑 Stopping servers...")
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            print("✅ Backend server stopped")
            
        if self.frontend_process:
            self.frontend_process.terminate()
            print("✅ Frontend server stopped")
    
    def monitor_processes(self):
        """Monitor server processes"""
        while self.running:
            time.sleep(5)
            
            # Check backend
            if self.backend_process and self.backend_process.poll() is not None:
                print("⚠️  Backend server stopped unexpectedly")
                if self.running:
                    print("🔄 Restarting backend server...")
                    self.start_backend()
            
            # Check frontend
            if self.frontend_process and self.frontend_process.poll() is not None:
                print("⚠️  Frontend server stopped unexpectedly")
                if self.running:
                    print("🔄 Restarting frontend server...")
                    self.start_frontend()
    
    def run(self):
        """Run both servers"""
        print("🎯 EVE Trading System - Frontend Manager")
        print("=" * 50)
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            print("\n🛑 Received interrupt signal")
            self.stop_servers()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start servers
        backend_ok = self.start_backend()
        frontend_ok = self.start_frontend()
        
        if not backend_ok or not frontend_ok:
            print("❌ Failed to start servers")
            return
        
        print("\n🎉 Both servers started successfully!")
        print("📊 Backend API: http://localhost:5000")
        print("🎮 Frontend Dashboard: http://localhost:3000")
        print("\n💡 Press Ctrl+C to stop both servers")
        print("=" * 50)
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        # Keep main thread alive
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_servers()

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check if frontend directory exists
    if not Path("frontend").exists():
        print("❌ Frontend directory not found")
        print("💡 Please run: mkdir frontend && cd frontend && npm install")
        return False
    
    # Check if node_modules exists
    if not Path("frontend/node_modules").exists():
        print("❌ Node modules not found")
        print("💡 Please run: cd frontend && npm install")
        return False
    
    # Check if Python dependencies are installed
    try:
        import flask
        import aiohttp
        import pandas
        print("✅ All dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("💡 Please run: pip install -r requirements.txt")
        return False

def main():
    """Main function"""
    print("🎯 EVE Trading System - Frontend Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Start servers
    manager = FrontendManager()
    manager.run()

if __name__ == "__main__":
    main() 
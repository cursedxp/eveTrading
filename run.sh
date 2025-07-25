#!/bin/bash

# EVE Trading System Runner Script
# This script ensures the correct Python interpreter is used

echo "🚀 Starting EVE Trading System..."

# Activate virtual environment and run with correct Python
source venv/bin/activate
./venv/bin/python master_runner.py "$@" 
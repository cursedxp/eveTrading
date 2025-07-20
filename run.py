#!/usr/bin/env python3
"""
Runner script for EVE Trading application
"""
import subprocess
import sys
import os

def main():
    # Get the virtual environment Python path
    venv_python = os.path.join(os.path.dirname(__file__), 'venv', 'bin', 'python')
    
    # Run the main script
    result = subprocess.run([venv_python, 'fetchMarketData.py'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error:", result.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 
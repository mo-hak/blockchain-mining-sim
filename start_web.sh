#!/bin/bash

# Blockchain Mining Simulation - Web Interface Startup Script

echo "======================================"
echo "Blockchain Mining Simulation"
echo "Web Interface Startup"
echo "======================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if required packages are installed
echo "Checking dependencies..."
python3 -c "import flask, flask_cors, matplotlib, numpy" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    python3 -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        exit 1
    fi
fi

echo "✓ Dependencies satisfied"
echo ""

# Start the Flask application
echo "Starting Flask server..."
echo "The web interface will be available at:"
echo ""
echo "    http://localhost:5001"
echo ""
echo "Note: Using port 5001 (port 5000 is often used by macOS AirPlay)"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 app.py


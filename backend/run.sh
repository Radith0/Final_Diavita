#!/bin/bash

# Diabetes Detection AI Backend - Quick Start Script

echo "Starting Diabetes Detection AI Backend..."

# Kill any existing process on port 5000
echo "Checking for existing processes on port 5000..."
PID=$(lsof -t -i:5000 2>/dev/null)
if [ -n "$PID" ]; then
    echo "Killing process $PID on port 5000..."
    kill -9 $PID 2>/dev/null
    sleep 1
    echo "Port 5000 cleared."
else
    echo "Port 5000 is available."
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Create necessary directories
echo "Creating directories..."
mkdir -p logs uploads models/retinal/weights models/lifestyle/weights

# Run the application
echo "Starting Flask server..."
python app.py

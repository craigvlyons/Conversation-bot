#!/bin/bash

# Cross-platform startup script for Conversation Bot (Unix/Linux/macOS)
echo "Starting Conversation Bot..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/lib/python3.*/site-packages/installed.txt" ]; then
    echo "Installing requirements..."
    pip install -r requirements.txt
    # Create a marker file to indicate requirements are installed
    touch "venv/lib/python3.*/site-packages/installed.txt" 2>/dev/null || true
fi

# Check for required environment variables
if [ -z "$GEMINI_KEY" ] && [ -z "$OPENAI_KEY" ]; then
    echo "Warning: No AI API keys found in environment variables."
    echo "Please set GEMINI_KEY and/or OPENAI_KEY in your .env file or environment."
fi

if [ -z "$PRORCUPINE_KEY" ]; then
    echo "Warning: PRORCUPINE_KEY not found. Wake word detection may not work."
fi

# Run the application
echo "Launching Conversation Bot..."
python main.py

# Keep terminal open on error (similar to Windows pause)
if [ $? -ne 0 ]; then
    echo "Press any key to continue..."
    read -n 1 -s
fi
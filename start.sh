#!/bin/bash

echo "🎮 UQ Party Queue Manager - Quick Start"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"
echo ""

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
fi

echo "🔌 Activating virtual environment..."
source venv/bin/activate

echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "🚀 Starting server..."
echo ""

python server.py --log="mock_game.log"


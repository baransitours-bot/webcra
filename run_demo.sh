#!/bin/bash

echo "🌍 Universal Immigration Crawler - Quick Start"
echo "=============================================="
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt --break-system-packages --quiet

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Running the crawler..."
echo ""

# Run the simple crawler
python3 simple_crawler.py

echo ""
echo "=============================================="
echo "✅ Demo complete!"
echo ""
echo "📁 Check these files:"
echo "   • data/crawled_pages.json - Crawled data"
echo "   • README.md - Documentation"
echo ""
echo "🧠 Try the LLM integration:"
echo "   python3 llm_integration_example.py"
echo ""

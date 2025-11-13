#!/bin/bash
# Launch Immigration Platform Web UI
# For Linux/Mac

echo "🌍 Starting Immigration Platform Web UI..."
echo ""

# Check if streamlit is installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "⚠️  Streamlit not installed. Installing..."
    pip install streamlit
fi

echo "✅ Launching UI on http://localhost:8501"
echo "📱 Access from other devices: http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Launch with network access
streamlit run app.py --server.address=0.0.0.0 --server.port=8501

#!/bin/bash

# Vendor Portal Startup Script

echo "🚀 Starting Vendor Portal..."
echo ""

# Check if we're in the portal directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found. Please run this script from the portal directory."
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Streamlit not found. Installing dependencies..."
    pip3 install -r requirements.txt
fi

echo "✅ Starting Streamlit application..."
echo ""
echo "📋 Portal will open in your browser at: http://localhost:8501"
echo "🔐 Admin Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run streamlit
streamlit run app.py

# Made with Bob

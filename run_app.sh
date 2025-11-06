#!/bin/bash

# Bhajan Search Streamlit App - Demo Script
# Šis skripts parāda, kā palaist bhajanu meklētāja aplikāciju

echo "🕉️ Bhajan Search - Streamlit App Setup"
echo "======================================="
echo ""

# Check if Python is installed
if command -v python3 &> /dev/null; then
    echo "✓ Python3 found: $(python3 --version)"
else
    echo "❌ Python3 not found. Please install Python 3.8 or newer."
    exit 1
fi

# Check if pip is installed
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 found"
else
    echo "❌ pip3 not found. Please install pip."
    exit 1
fi

echo ""
echo "📦 Installing required packages..."
echo "================================="

# Install requirements
pip3 install streamlit pandas openpyxl

echo ""
echo "🚀 Starting Streamlit app..."
echo "============================"
echo ""
echo "Your bhajan search app will open in your default web browser."
echo "If it doesn't open automatically, go to: http://localhost:8501"
echo ""
echo "To stop the app, press Ctrl+C in this terminal."
echo ""

# Run the Streamlit app
streamlit run bhajan_streamlit_app.py

echo ""
echo "Thank you for using Bhajan Search! 🙏"
echo "Hare Kṛṣṇa! 🕉️"

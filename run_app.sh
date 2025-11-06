#!/bin/bash

# Bhajan Search Streamlit App - Fixed Data Version
# Šis skripts parāda, kā palaist bhajanu meklētāja aplikāciju ar fiksētiem datiem

echo "🕉️ Bhajan Search - Streamlit App (Fixed Data Version)"
echo "====================================================="
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

# Check if Bhajans.xlsx exists
if [ -f "Bhajans.xlsx" ]; then
    echo "✓ Bhajans.xlsx found"
else
    echo "⚠️  Bhajans.xlsx not found in current directory"
    echo "   Make sure to place your Excel file in the same folder as this script"
    echo "   The file must be named exactly 'Bhajans.xlsx'"
    echo ""
    echo "Expected file structure:"
    echo "bhajan-search/"
    echo "├── bhajan_streamlit_app.py"
    echo "├── data_loader.py"
    echo "├── Bhajans.xlsx          # Your Excel file here!"
    echo "├── requirements.txt"
    echo "└── run_app.sh"
    echo ""
    read -p "Do you want to continue with sample data? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
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
echo "Features:"
echo "- 📚 Browse by Title (A-Z)"
echo "- 📁 Browse by Category" 
echo "- 👤 Browse by Author"
echo "- 🇬🇧 Original/English text toggle"
echo "- 📱 Mobile-friendly design"
echo ""
echo "To stop the app, press Ctrl+C in this terminal."
echo ""

# Run the Streamlit app
streamlit run bhajan_streamlit_app.py

echo ""
echo "Thank you for using Bhajan Search! 🙏"
echo "Hare Kṛṣṇa! 🕉️"

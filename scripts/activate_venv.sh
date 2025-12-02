#!/bin/bash
# Quick activation script for Linux/Mac

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: bash scripts/setup_venv.sh"
    exit 1
fi

source venv/bin/activate
echo "✅ Virtual environment activated!"
echo "You can now run: python run.py"


#!/bin/bash

# AI Pathfinding Game Runner Script
# This script runs the pathfinding game with proper environment setup

echo "==================================================="
echo "    AI Pathfinding Game - Launch Script"
echo "==================================================="

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found!"
    print_status "Please run setup first: bash setup_game.sh"
    exit 1
fi

# Check if scripts directory exists
if [ ! -d "scripts" ]; then
    print_error "Scripts directory not found!"
    print_status "Make sure all game files are in the 'scripts/' directory"
    exit 1
fi

# Check if main game file exists
if [ ! -f "scripts/pathfinding_game.py" ]; then
    print_error "Game launcher not found in scripts/ directory!"
    exit 1
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source .venv/bin/activate

# Check Python and dependencies
print_status "Verifying dependencies..."
python3 -c "
import sys
import os
sys.path.insert(0, 'scripts')

try:
    import matplotlib
    import numpy
    import tkinter
    print('✓ All dependencies available')
except ImportError as e:
    print(f'✗ Missing dependency: {e}')
    print('Please run: bash setup_game.sh')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    print_error "Dependency check failed!"
    exit 1
fi

print_success "Environment ready!"
print_status "Starting AI Pathfinding Game..."
echo ""

# Add scripts directory to Python path and run the game
export PYTHONPATH="$SCRIPT_DIR/scripts:$PYTHONPATH"
cd scripts

# Try to run the game with error handling
python3 pathfinding_game.py

# Check exit status
EXIT_CODE=$?
echo ""
if [ $EXIT_CODE -eq 0 ]; then
    print_success "Game closed normally"
else
    print_warning "Game exited with code: $EXIT_CODE"
fi

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "==================================================="
print_status "Thanks for playing!"
echo "==================================================="

#!/bin/bash

# AI Pathfinding Game Setup Script
# This script creates a virtual environment and installs dependencies

echo "==================================================="
echo "    AI Pathfinding Game - Setup Script"
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

# Check if Python 3 is installed
print_status "Checking Python 3 installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
print_success "Python ${PYTHON_VERSION} found"

# Check if pip is installed
print_status "Checking pip installation..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip3 first."
    echo "On Ubuntu/Debian: sudo apt install python3-pip"
    exit 1
fi

# Check and install tkinter if needed (Linux only)
print_status "Checking tkinter availability..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    print_warning "tkinter not found. Attempting to install..."
    if command -v apt-get &> /dev/null; then
        print_status "Installing python3-tk using apt..."
        sudo apt-get update
        sudo apt-get install -y python3-tk
    elif command -v yum &> /dev/null; then
        print_status "Installing tkinter using yum..."
        sudo yum install -y tkinter
    else
        print_warning "Please install tkinter manually for your system"
    fi
fi

# Create virtual environment
print_status "Setting up virtual environment..."
if [ -d ".venv" ]; then
    print_status "Virtual environment already exists. Checking if it's working..."
    if .venv/bin/python -c "import sys; print('Python', sys.version)" 2>/dev/null; then
        print_success "Existing virtual environment is working"
    else
        print_warning "Existing virtual environment appears broken. Recreating..."
        rm -rf .venv
        python3 -m venv .venv
    fi
else
    print_status "Creating new virtual environment..."
    python3 -m venv .venv
fi

if [ $? -eq 0 ] && [ -d ".venv" ]; then
    print_success "Virtual environment ready"
else
    print_error "Failed to create virtual environment"
    exit 1
fi

# Install dependencies
print_status "Checking and installing required packages..."
source .venv/bin/activate

# Check what's already installed
missing_packages=""

# Check matplotlib
if ! python -c "import matplotlib" 2>/dev/null; then
    missing_packages="$missing_packages matplotlib"
fi

# Check numpy  
if ! python -c "import numpy" 2>/dev/null; then
    missing_packages="$missing_packages numpy"
fi

if [ -z "$missing_packages" ]; then
    print_success "All required packages are already installed"
else
    print_status "Installing missing packages:$missing_packages"
    # Upgrade pip first if needed
    pip install --upgrade pip --quiet
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        pip install matplotlib numpy
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Dependencies installed successfully"
    else
        print_error "Failed to install some dependencies"
        exit 1
    fi
fi

# Test the installation
print_status "Testing installation..."
python3 -c "
import sys
import os
sys.path.append('scripts')

try:
    import matplotlib
    import numpy
    import tkinter
    # Test if we can import the game modules
    from pathfinding_backend import GridGameEngine
    print('✓ All required packages and modules are working')
except ImportError as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    print_success "Installation test passed!"
else
    print_error "Installation test failed!"
    exit 1
fi

echo ""
echo "==================================================="
print_success "Setup completed successfully!"
echo "==================================================="
echo ""
echo "Next steps:"
echo "1. Run the game: ./run_game.sh"
echo "2. Or activate environment manually: source .venv/bin/activate"
echo ""
print_status "Game files are located in the 'scripts/' directory"
print_status "Virtual environment created in '.venv/' directory"
echo ""

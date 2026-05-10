#!/bin/bash
#
# Setup script for Linux Kernel Update Tracker
#

set -e

echo "======================================"
echo "Linux Kernel Update Tracker Setup"
echo "======================================"
echo

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.10"

if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)"; then
    echo "Error: Python 3.10 or higher required (found $python_version)"
    exit 1
fi
echo "✓ Python $python_version"
echo

# Check for Claude API key
echo "Checking for Anthropic API key..."
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠ ANTHROPIC_API_KEY environment variable not set"
    echo
    echo "Please set your API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    echo
    echo "You can get an API key from: https://console.anthropic.com/"
    echo
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✓ API key found"
fi
echo

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Created venv/"
else
    echo "✓ venv/ already exists"
fi
echo

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo

# Create directory structure
echo "Creating directory structure..."
mkdir -p data/{raw,processed,drafts,published}
mkdir -p data/repos
mkdir -p database
echo "✓ Directories created"
echo

# Make scripts executable
echo "Making scripts executable..."
chmod +x agents/*.py
chmod +x scripts/*.sh
echo "✓ Scripts are executable"
echo

# Test imports
echo "Testing Python imports..."
python3 -c "import anthropic; import requests; import dateutil" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ Core imports successful"
else
    echo "⚠ Import test failed"
fi
echo

# Summary
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo
echo "Next steps:"
echo
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo
echo "2. Set your API key (if not already set):"
echo "   export ANTHROPIC_API_KEY='your-key-here'"
echo
echo "3. Test data collection:"
echo "   python3 agents/collector.py --subsystem xfs --days 7"
echo
echo "4. Analyze collected data:"
echo "   python3 agents/analyzer.py --subsystem xfs"
echo
echo "5. See PROJECT_PLAN.md for the full roadmap"
echo

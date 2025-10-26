#!/bin/bash
# Activation script for Street View Hyperlapse Python 3.13 environment
# Created: September 24, 2025

echo "🚀 Activating Street View Hyperlapse environment..."

# Navigate to project directory
cd "$(dirname "$0")"

# Activate the Python 3.13 virtual environment
source .venv_python313/bin/activate

echo "✅ Environment activated!"
echo "🐍 Python: $(python --version)"
echo "📦 Packages: OpenCV, MoviePy, Pillow, Playwright, Jupyter"
echo ""
echo "💡 Usage:"
echo "   jupyter notebook                    # Start Jupyter"
echo "   python your_script.py              # Run Python scripts"
echo "   playwright install chromium         # Install browsers (if needed)"
echo ""
echo "🎬 Ready for Street View Hyperlapse creation!"

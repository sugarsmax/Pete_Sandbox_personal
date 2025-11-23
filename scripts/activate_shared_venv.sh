#!/bin/bash
# Shared venv activation script
# Source this from any project directory: source ~/.python-venvs/pdms-shared/bin/activate
# Or use this as a template for project-specific activation scripts

SHARED_VENV="$HOME/.python-venvs/pdms-shared"

if [ ! -d "$SHARED_VENV" ]; then
    echo "❌ Error: Shared venv not found at $SHARED_VENV"
    echo "📍 Create it with: python3.14 -m venv $SHARED_VENV"
    return 1
fi

# Activate the shared venv
source "$SHARED_VENV/bin/activate"

echo "✅ Shared venv activated!"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"
echo ""
echo "💡 View packages: pip list"
echo "💡 Install package: pip install package_name"


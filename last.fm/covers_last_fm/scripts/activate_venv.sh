#!/bin/bash
# Activates the appropriate Python virtual environment for this project
# Priority order:
#  1. ~/python/venv (local machine override)
#  2. /Users/maxfiep/.python-venvs/pdms-shared (shared team venv)
#  3. COVERS_VENV environment variable (if set)
#  4. Creates a local venv if none exist

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL_VENV="$HOME/python/venv"
SHARED_VENV="/Users/maxfiep/.python-venvs/pdms-shared"
CUSTOM_VENV="${COVERS_VENV:-}"

# Function to check if venv exists and activate it
activate_if_exists() {
    local venv_path="$1"
    local name="$2"
    
    if [ -f "$venv_path/bin/activate" ]; then
        echo "[covers_last_fm] Activating $name at: $venv_path"
        source "$venv_path/bin/activate"
        return 0
    fi
    return 1
}

# Try activation in priority order
if [ -n "$CUSTOM_VENV" ] && activate_if_exists "$CUSTOM_VENV" "custom (COVERS_VENV)"; then
    :
elif activate_if_exists "$LOCAL_VENV" "local override"; then
    :
elif activate_if_exists "$SHARED_VENV" "shared team venv"; then
    :
else
    # No venv found - offer to create one
    echo ""
    echo "[covers_last_fm] No Python virtual environment found."
    echo ""
    echo "Available options:"
    echo "  1. Use local venv at: $LOCAL_VENV (requires setup)"
    echo "  2. Use shared venv at: $SHARED_VENV (requires setup)"
    echo "  3. Create a new venv in this project"
    echo ""
    read -p "Create new venv in project directory? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv "$PROJECT_DIR/.venv"
        source "$PROJECT_DIR/.venv/bin/activate"
        echo "[covers_last_fm] Created and activated venv at: $PROJECT_DIR/.venv"
        echo ""
        echo "Installing requirements..."
        pip install --upgrade pip
        pip install requests beautifulsoup4 pyyaml playwright
        playwright install chromium
        echo "[covers_last_fm] Setup complete!"
    else
        echo "[covers_last_fm] Activation skipped. Please set up a venv manually."
        exit 1
    fi
fi

echo "[covers_last_fm] Python: $(which python)"
echo "[covers_last_fm] Version: $(python --version)"


#!/usr/bin/env bash

# Exit on error
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Define Downloads path
if [[ "$OSTYPE" == "darwin"* ]]; then
    DL_DIR="$HOME/Downloads"
else
    # Fallback to standard xdg user dir if available, otherwise ~/Downloads
    if command -v xdg-user-dir &> /dev/null; then
        DL_DIR="$(xdg-user-dir DOWNLOAD)"
    else
        DL_DIR="$HOME/Downloads"
    fi
fi

# Define Cache and Venv paths
CACHE_DIR="$DL_DIR/html2md-cache/wheels"
# Create a temporary directory that will be deleted on exit
VENV_DIR=$(mktemp -d "$DL_DIR/html2md-venv-XXXXXX")

echo "[INFO] Using cache directory: $CACHE_DIR"
echo "[INFO] Creating temporary virtual environment: $VENV_DIR"

# Setup cleanup trap to delete the venv when the script exits
cleanup() {
    echo "[INFO] Cleaning up temporary virtual environment..."
    rm -rf "$VENV_DIR"
}
trap cleanup EXIT

# Find python
if command -v python3 &> /dev/null; then
    PYTHON="python3"
elif command -v python &> /dev/null; then
    PYTHON="python"
else
    echo "[ERROR] Python 3 not found."
    exit 1
fi

# Create the temporary virtual environment
$PYTHON -m venv "$VENV_DIR"
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "[ERROR] Failed to create virtual environment."
    exit 1
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Upgrade pip and wheel (quietly)
python -m pip install --upgrade pip wheel >/dev/null 2>&1

# Check if cache needs to be populated
if [ ! -d "$CACHE_DIR" ] || [ -z "$(ls -A "$CACHE_DIR")" ]; then
    echo "[INFO] Cache is empty. Downloading and building wheels to $CACHE_DIR..."
    mkdir -p "$CACHE_DIR"
    if ! pip wheel . -w "$CACHE_DIR"; then
        echo "[ERROR] Failed to build wheels. Check your internet connection or dependencies."
        exit 1
    fi
else
    echo "[INFO] Found cached wheels in $CACHE_DIR."
fi

# Install from cache purely offline
echo "[INFO] Installing package from local cache..."
if ! pip install html2md-cli --no-index --find-links="$CACHE_DIR" >/dev/null 2>&1; then
    echo "[ERROR] Failed to install from cache. The cache might be incomplete. Try deleting $CACHE_DIR and running again."
    exit 1
fi

# Pass all args through to html2md
echo "[INFO] Running html2md..."
html2md "$@"

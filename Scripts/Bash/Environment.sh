#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROUTES_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

REQUIRED_VERSION=1

# Create or update Settings.sh if outdated
source "$SCRIPT_DIR/Settings.sh" 2>/dev/null || SETTINGS_VERSION=0

if [ "$SETTINGS_VERSION" -lt "$REQUIRED_VERSION" ]; then
    cp "$SCRIPT_DIR/Settings.template.sh" "$SCRIPT_DIR/Settings.sh"
    echo "=========================================="
    echo "Settings.sh created/updated from template."
    echo "Please edit it in:"
    echo "  $SCRIPT_DIR/Settings.sh"
    echo "=========================================="
    exit 1
fi

source "$SCRIPT_DIR/Settings.sh"

# Check ogr2ogr dependency
if ! command -v ogr2ogr &> /dev/null; then
    echo "Error: ogr2ogr not found. Please install GDAL."
    echo "  macOS: brew install gdal"
    echo "  Ubuntu/Debian: sudo apt install gdal-bin"
    exit 1
fi

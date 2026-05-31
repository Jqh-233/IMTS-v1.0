#!/bin/bash
# IMTS Server — Linux cloud deployment launcher
# Usage: bash start-server.sh

set -e
cd "$(dirname "$0")"

echo "========================================"
echo "  IMTS Server Setup"
echo "========================================"
echo ""

# 1. Check Python
echo "[1/4] Checking Python..."
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo "[ERROR] Python 3.10+ not found."
    echo "Install: sudo apt install python3 python3-venv python3-pip"
    exit 1
fi
echo "  [OK] $($PYTHON --version)"

# 2. Setup venv + deps
echo "[2/4] Setting up environment..."
if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
fi
source .venv/bin/activate
if [ ! -f ".venv/.deps_installed" ]; then
    echo "  Installing dependencies..."
    pip install -r backend/requirements.txt -q
    touch .venv/.deps_installed
fi
echo "  [OK] Dependencies ready"

# 3. Verify frontend
echo "[3/4] Checking frontend..."
if [ ! -d "frontend/dist" ]; then
    echo "  [WARN] frontend/dist/ not found."
    echo "  Build it locally with: cd frontend && npm run build"
    echo "  Then upload the dist/ folder."
    echo "  Starting backend-only (API docs available)."
fi
echo "  [OK] Ready"

# 4. Start
echo "[4/4] Starting server..."
echo ""
echo "  IMTS running on http://0.0.0.0:8501"
echo "  Press Ctrl+C to stop."
echo ""

.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8501

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

# 2. Setup venv + deps (always reinstall to catch new deps)
echo "[2/4] Installing dependencies..."
if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
fi
source .venv/bin/activate
pip install -r backend/requirements.txt -q
echo "  [OK] Dependencies ready"

# 3. Database migration
echo "[3/4] Running database migration..."
if [ -f "imts_demo.db" ]; then
    # Existing DB: stamp current state so Alembic knows tables already exist
    cd backend
    python -m alembic -c alembic.ini stamp head 2>/dev/null || echo "  (stamp skipped, will upgrade)"
    cd ..
else
    # Fresh DB: Alembic will create tables on first startup
    echo "  New database will be created on startup"
fi
echo "  [OK] Migration ready"

# 4. Check frontend
if [ ! -d "frontend/dist" ]; then
    echo "  [WARN] frontend/dist/ not found — build it locally with: cd frontend && npm run build"
fi

# 5. Start
echo "[4/4] Starting server..."
echo ""
echo "  IMTS running on http://0.0.0.0:8501"
echo "  Press Ctrl+C to stop."
echo ""

.venv/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8501

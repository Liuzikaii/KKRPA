#!/bin/bash
# KKRPA Desktop Build Script
# Builds the complete .exe package

set -e

echo "╔═══════════════════════════════════════╗"
echo "║     KKRPA Desktop Build Script        ║"
echo "╚═══════════════════════════════════════╝"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$SCRIPT_DIR"

# ─── Step 1: Build Frontend ───────────────────
echo ""
echo "📦 Step 1: Building Next.js frontend (static export)..."
cd "$ROOT_DIR/frontend"
npm ci
npm run build
echo "✅ Frontend built → frontend/out/"

# ─── Step 2: Build Backend ────────────────────
echo ""
echo "🐍 Step 2: Packaging Python backend with PyInstaller..."
cd "$ROOT_DIR/backend"

# Create/activate venv
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt

# Run PyInstaller
pyinstaller \
    --name kkrpa-server \
    --onefile \
    --hidden-import=app.models.user \
    --hidden-import=app.models.workflow \
    --hidden-import=app.models.task \
    --hidden-import=app.models.schedule \
    --hidden-import=app.api.auth \
    --hidden-import=app.api.workflows \
    --hidden-import=app.api.tasks \
    --hidden-import=app.api.schedules \
    --hidden-import=app.api.license \
    --hidden-import=app.engine.nodes.python_node \
    --hidden-import=app.engine.nodes.http_node \
    --hidden-import=app.engine.nodes.condition_node \
    --hidden-import=app.engine.nodes.loop_node \
    --hidden-import=app.engine.nodes.delay_node \
    --hidden-import=aiosqlite \
    --hidden-import=uvicorn.logging \
    --hidden-import=uvicorn.protocols.http \
    --hidden-import=uvicorn.protocols.http.auto \
    --hidden-import=uvicorn.protocols.websockets \
    --hidden-import=uvicorn.protocols.websockets.auto \
    --hidden-import=uvicorn.lifespan \
    --hidden-import=uvicorn.lifespan.on \
    --add-data "app:app" \
    --clean \
    app/main.py

deactivate
echo "✅ Backend packaged → backend/dist/kkrpa-server"

# ─── Step 3: Build Electron App ───────────────
echo ""
echo "⚡ Step 3: Building Electron app..."
cd "$ROOT_DIR/electron"
npm ci
npm run build:win
echo "✅ Electron app built → dist/"

# ─── Done ─────────────────────────────────────
echo ""
echo "╔═══════════════════════════════════════╗"
echo "║          Build Complete! 🎉           ║"
echo "║  Output: dist/KKRPA Setup *.exe       ║"
echo "╚═══════════════════════════════════════╝"

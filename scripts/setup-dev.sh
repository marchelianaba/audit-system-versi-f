#!/usr/bin/env bash
# Setup lokal pengembangan.
# Jalankan dari folder audit-system-v7/.
#
# Cross-platform:
#   - macOS / Linux: bash scripts/setup-dev.sh
#   - Windows (Git Bash): bash scripts/setup-dev.sh
#   - Windows (PowerShell native, tanpa Git Bash): pakai scripts\setup-dev.ps1

set -euo pipefail
cd "$(dirname "$0")/.."

echo "🔧 Setup audit-system-v7 untuk dev lokal..."

# 1. .env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ .env dibuat dari .env.example — silakan edit dan isi ANTHROPIC_API_KEY"
else
    echo "ℹ️  .env sudah ada, skip"
fi

# 2. Docker Postgres
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker tidak berjalan. Mulai Docker Desktop dulu."
    exit 1
fi

docker compose up -d db
echo "⏳ Menunggu Postgres siap..."
sleep 5

# 3. Backend deps
cd backend

# Resolusi perintah Python: di Windows umumnya `python` (bukan `python3`).
PYTHON_CMD=""
for cand in python3 python py; do
    if command -v "$cand" > /dev/null 2>&1; then
        PYTHON_CMD="$cand"
        break
    fi
done
if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Tidak menemukan python3 / python / py di PATH. Install Python 3.11+ dulu."
    exit 1
fi
echo "🐍 Pakai Python: $PYTHON_CMD ($($PYTHON_CMD --version 2>&1))"

if [ ! -d ".venv" ]; then
    "$PYTHON_CMD" -m venv .venv
fi

# Resolusi script activate venv: Unix → bin/activate; Windows → Scripts/activate.
if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
    # Windows venv via Git Bash
    # shellcheck disable=SC1091
    source .venv/Scripts/activate
else
    echo "❌ Tidak menemukan script activate venv (.venv/bin/activate atau .venv/Scripts/activate)."
    exit 1
fi

pip install --upgrade pip
pip install -r requirements.txt

# 4. Init DB
export DATABASE_URL="postgresql+asyncpg://audit:audit@localhost:5432/audit_v7"
python -m app.init_db
deactivate

# 5. Frontend deps
cd ../frontend
npm install
if [ ! -f .env.local ]; then
    cp .env.example .env.local
fi

echo ""
echo "✅ Setup selesai."
echo ""
echo "Untuk menjalankan dev server:"
if [ -f ../backend/.venv/Scripts/activate ]; then
    echo "  Terminal 1: cd backend && source .venv/Scripts/activate && uvicorn app.main:app --reload"
else
    echo "  Terminal 1: cd backend && source .venv/bin/activate && uvicorn app.main:app --reload"
fi
echo "  Terminal 2: cd frontend && npm run dev"
echo ""
echo "Buka http://localhost:3000"

#!/usr/bin/env bash
# Start backend dev server dengan ANTHROPIC_API_KEY ter-export ke environment.
#
# Kenapa perlu: claude-agent-sdk men-spawn `claude` CLI sebagai subprocess.
# CLI butuh auth. Kalau OAuth Claude.ai sudah di-logout (`claude auth logout`),
# CLI HARUS dapat ANTHROPIC_API_KEY dari environment proses uvicorn. pydantic
# memuat .env untuk config app, TAPI tidak meng-export ANTHROPIC_API_KEY ke
# environment untuk subprocess — jadi kita export manual di sini.
#
# Pakai:
#   - macOS / Linux:          bash scripts/dev-backend.sh   (Ctrl+C untuk stop)
#   - Windows (Git Bash):     bash scripts/dev-backend.sh
#   - Windows (PowerShell):   scripts\dev-backend.ps1
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT/backend"

# `.env` di backend/ — kalau pakai symlink (Unix), file akan resolve. Di Windows
# (yang tak punya symlink tanpa admin), jatuh ke project-root .env.
ENV_FILE=""
if [ -f .env ]; then
    ENV_FILE=".env"
elif [ -f "$PROJECT_ROOT/.env" ]; then
    ENV_FILE="$PROJECT_ROOT/.env"
    echo "ℹ️  backend/.env tidak ada, fallback ke project-root .env: $ENV_FILE"
else
    echo "❌ Tidak menemukan .env (cek backend/.env atau project-root .env). Lihat README gotcha #1."
    exit 1
fi

# Ambil ANTHROPIC_API_KEY dari .env dan export agar subprocess claude CLI mewarisinya.
# `tr -d '[:space:]'` ikut menghapus CR di akhir baris (Windows CRLF).
KEY="$(grep -E '^ANTHROPIC_API_KEY=' "$ENV_FILE" | head -1 | cut -d= -f2- | tr -d '[:space:]')"
if [ -z "$KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY tidak ditemukan di $ENV_FILE."
    echo "    Agen akan gagal auth kecuali Anda 'claude auth login' (OAuth)."
else
    export ANTHROPIC_API_KEY="$KEY"
    echo "✅ ANTHROPIC_API_KEY ter-export (${KEY:0:14}…). claude CLI akan pakai API key."
fi

# Aktifkan venv — Unix → bin/activate; Windows → Scripts/activate (Git Bash style).
if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
elif [ -f .venv/Scripts/activate ]; then
    # shellcheck disable=SC1091
    source .venv/Scripts/activate
fi

exec uvicorn app.main:app --reload --port 8000

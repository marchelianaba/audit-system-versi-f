# Start backend dev server dgn ANTHROPIC_API_KEY di-set ke environment proses.
# Windows PowerShell equivalent of dev-backend.sh.
#
# Kenapa perlu: claude-agent-sdk men-spawn `claude` CLI sebagai subprocess.
# CLI butuh auth. Kalau OAuth Claude.ai sudah di-logout, CLI HARUS dapat
# ANTHROPIC_API_KEY dari environment proses uvicorn. pydantic memuat .env untuk
# config app, TAPI tidak meng-export ANTHROPIC_API_KEY ke environment untuk
# subprocess - jadi kita set manual di sini.
#
# Pakai (PowerShell, dari folder audit-system-v7):
#   .\scripts\dev-backend.ps1            (Ctrl+C untuk stop) — agen AI BISA jalan
#   .\scripts\dev-backend.ps1 -Reload    hot-reload, tapi agen AI TIDAK bisa jalan
#
# ============================================================================
# KENAPA --reload TIDAK LAGI DEFAULT DI WINDOWS (9 Agu 2026)
# ============================================================================
# Dengan `--reload`, uvicorn menyalakan mode multiproses (`use_subprocess`), dan
# di Windows itu memaksa `WindowsSelectorEventLoopPolicy`
# (uvicorn/loops/asyncio.py). SelectorEventLoop di Windows TIDAK MENDUKUNG
# pembuatan subprocess — `loop.subprocess_exec` melempar NotImplementedError.
#
# claude-agent-sdk menjalankan agen dengan men-spawn CLI `claude` sebagai
# subprocess asyncio. Akibatnya, setiap run agen AT/KT gagal dengan pesan:
#
#     Failed to start Claude Code:
#
# Pesan itu MENYESATKAN — terlihat seperti CLI belum terpasang, padahal CLI ada
# dan sehat; yang salah adalah event loop-nya. Tanpa `--reload`, Python memakai
# ProactorEventLoop (default Windows) yang mendukung subprocess, dan agen jalan.
#
# Konsekuensi: perubahan kode backend perlu restart manual. Untuk kerja
# UI/endpoint yang tidak menyentuh agen, pakai -Reload agar hot-reload aktif.
# Di macOS/Linux masalah ini tidak ada (uvicorn tidak mengganti policy).
# ============================================================================

param(
    # Aktifkan hot-reload. HANYA untuk kerja yang tidak menjalankan agen AI.
    [switch]$Reload
)

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $ProjectRoot 'backend')

# `.env` di backend/ — di Windows symlink butuh admin, jadi cari ke backend/.env
# dulu, kalau tidak ada fallback ke project-root .env.
$EnvFile = $null
if (Test-Path '.env') {
    $EnvFile = (Resolve-Path '.env').Path
} elseif (Test-Path (Join-Path $ProjectRoot '.env')) {
    $EnvFile = (Resolve-Path (Join-Path $ProjectRoot '.env')).Path
    Write-Host "[..] backend\.env tidak ada, fallback ke project-root .env: $EnvFile"
} else {
    Write-Error "Tidak menemukan .env (cek backend\.env atau project-root .env). Lihat README gotcha #1."
    exit 1
}

# Ambil ANTHROPIC_API_KEY dari .env (toleran CRLF & whitespace).
$Key = $null
$lines = Get-Content $EnvFile -ErrorAction SilentlyContinue
foreach ($line in $lines) {
    if ($line -match '^\s*ANTHROPIC_API_KEY\s*=\s*(.+?)\s*$') {
        $Key = $Matches[1].Trim()
        # Strip optional surrounding quotes
        if ($Key.StartsWith('"') -and $Key.EndsWith('"')) { $Key = $Key.Substring(1, $Key.Length - 2) }
        elseif ($Key.StartsWith("'") -and $Key.EndsWith("'")) { $Key = $Key.Substring(1, $Key.Length - 2) }
        break
    }
}
if ([string]::IsNullOrWhiteSpace($Key)) {
    Write-Host "[..] ANTHROPIC_API_KEY kosong di $EnvFile (normal untuk mode langganan)."
} else {
    $env:ANTHROPIC_API_KEY = $Key
    $prefix = if ($Key.Length -ge 14) { $Key.Substring(0, 14) } else { $Key }
    Write-Host "[OK] ANTHROPIC_API_KEY ter-set ($prefix...). claude CLI akan pakai API key." -ForegroundColor Green
}

# Mode langganan: build_agent_options membaca CLAUDE_CODE_OAUTH_TOKEN dari
# ENVIRONMENT PROSES (app/agents/base.py), bukan dari settings pydantic — jadi
# token di .env harus di-export manual seperti halnya ANTHROPIC_API_KEY.
$Oauth = $null
foreach ($line in $lines) {
    if ($line -match '^\s*CLAUDE_CODE_OAUTH_TOKEN\s*=\s*(.+?)\s*$') {
        $Oauth = $Matches[1].Trim()
        if ($Oauth.StartsWith('"') -and $Oauth.EndsWith('"')) { $Oauth = $Oauth.Substring(1, $Oauth.Length - 2) }
        elseif ($Oauth.StartsWith("'") -and $Oauth.EndsWith("'")) { $Oauth = $Oauth.Substring(1, $Oauth.Length - 2) }
        break
    }
}
if (-not [string]::IsNullOrWhiteSpace($Oauth)) {
    $env:CLAUDE_CODE_OAUTH_TOKEN = $Oauth
    Write-Host "[OK] CLAUDE_CODE_OAUTH_TOKEN ter-set. Agen akan pakai kuota LANGGANAN, bukan kredit API." -ForegroundColor Green
} elseif ([string]::IsNullOrWhiteSpace($Key)) {
    Write-Host "[..] Tanpa API key & tanpa OAuth token — agen mengandalkan login tersimpan 'claude login'."
    Write-Host "     Belum pernah login? Jalankan sekali:  claude setup-token   (lalu tempel hasilnya ke .env)"
}

# Activate venv (Windows venv → Scripts\Activate.ps1)
if (Test-Path '.venv\Scripts\Activate.ps1') {
    & '.venv\Scripts\Activate.ps1'
} elseif (Test-Path '.venv\bin\Activate.ps1') {
    & '.venv\bin\Activate.ps1'
} else {
    Write-Warning ".venv tidak ditemukan. Jalankan scripts\setup-dev.ps1 dulu, atau buat venv manual."
}

if ($Reload) {
    Write-Warning "Mode -Reload: hot-reload AKTIF, tetapi agen AI (AT/KT) TIDAK akan bisa jalan."
    Write-Host  "          Penyebab: uvicorn --reload memaksa SelectorEventLoop di Windows, yang" -ForegroundColor DarkYellow
    Write-Host  "          tidak bisa men-spawn subprocess `claude`. Jalankan tanpa -Reload untuk menguji agen." -ForegroundColor DarkYellow
    uvicorn app.main:app --reload --port 8000
} else {
    Write-Host "[OK] Jalan tanpa --reload -> agen AI bisa men-spawn CLI claude." -ForegroundColor Green
    Write-Host "     Ubah kode backend? Restart manual (Ctrl+C lalu jalankan lagi)."
    Write-Host "     Butuh hot-reload & tidak menguji agen: .\scripts\dev-backend.ps1 -Reload"
    uvicorn app.main:app --port 8000
}

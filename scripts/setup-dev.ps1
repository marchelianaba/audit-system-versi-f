# Setup lokal pengembangan — Windows PowerShell equivalent of setup-dev.sh.
#
# Pakai (PowerShell, dari folder audit-system-v7):
#   .\scripts\setup-dev.ps1
#
# Jika PowerShell menolak ("execution policy"), jalankan sekali:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

Write-Host "Setup audit-system-v7 untuk dev lokal..." -ForegroundColor Cyan

# 1. .env
if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
    Write-Host "[OK] .env dibuat dari .env.example - silakan edit dan isi ANTHROPIC_API_KEY" -ForegroundColor Green
} else {
    Write-Host "[..] .env sudah ada, skip"
}

# 2. Docker Postgres
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker tidak berjalan. Mulai Docker Desktop dulu."
    exit 1
}

docker compose up -d db
if ($LASTEXITCODE -ne 0) {
    Write-Error "docker compose up gagal."
    exit 1
}

Write-Host "Menunggu Postgres siap..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 3. Backend deps
Set-Location backend

# Resolusi perintah Python: Windows umumnya `python` (atau `py`).
$PythonCmd = $null
foreach ($cand in 'python', 'python3', 'py') {
    $found = Get-Command $cand -ErrorAction SilentlyContinue
    if ($found) { $PythonCmd = $cand; break }
}
if (-not $PythonCmd) {
    Write-Error "Tidak menemukan python / python3 / py di PATH. Install Python 3.11+ dulu."
    exit 1
}
Write-Host "[..] Pakai Python: $PythonCmd ($(& $PythonCmd --version 2>&1))"

if (-not (Test-Path '.venv')) {
    & $PythonCmd -m venv .venv
}

# Activate venv (PowerShell)
if (Test-Path '.venv\Scripts\Activate.ps1') {
    & '.venv\Scripts\Activate.ps1'
} elseif (Test-Path '.venv\bin\Activate.ps1') {
    & '.venv\bin\Activate.ps1'
} else {
    Write-Error "Tidak menemukan .venv\Scripts\Activate.ps1. Cek venv terbuat dengan benar."
    exit 1
}

pip install --upgrade pip
pip install -r requirements.txt

# 4. Init DB
$env:DATABASE_URL = 'postgresql+asyncpg://audit:audit@localhost:5432/audit_v7'
python -m app.init_db

# Deactivate venv (best-effort - function ada setelah Activate.ps1 di-load)
if (Get-Command deactivate -ErrorAction SilentlyContinue) { deactivate }

# 5. Frontend deps
Set-Location ..\frontend
npm install
if (-not (Test-Path '.env.local')) {
    Copy-Item '.env.example' '.env.local'
}

Set-Location $ProjectRoot

Write-Host ""
Write-Host "[OK] Setup selesai." -ForegroundColor Green
Write-Host ""
Write-Host "Untuk menjalankan dev server:"
Write-Host "  Terminal 1: .\scripts\dev-backend.ps1"
Write-Host "              (atau manual: cd backend; .\.venv\Scripts\Activate.ps1; uvicorn app.main:app --reload)"
Write-Host "  Terminal 2: cd frontend; npm run dev"
Write-Host ""
Write-Host "Buka http://localhost:3000"

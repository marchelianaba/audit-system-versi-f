# Deployment script untuk Fly.io - Windows PowerShell equivalent of deploy-fly.sh.
#
# Pakai (PowerShell, dari folder audit-system-v7):
#   .\scripts\deploy-fly.ps1

$ErrorActionPreference = 'Stop'

if (-not (Get-Command fly -ErrorAction SilentlyContinue)) {
    Write-Error "flyctl belum terinstall. Install dulu: https://fly.io/docs/hands-on/install-flyctl/"
    exit 1
}

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $ProjectRoot 'backend')

Write-Host "Memverifikasi V6 sudah ter-embed di backend\v6\..." -ForegroundColor Cyan

# V6 sudah ter-embed di backend/v6/. Dockerfile akan COPY v6/ /v6/ langsung.
$Missing = @()
foreach ($sub in 'scripts', 'skills', 'templates', 'checklists') {
    if (-not (Test-Path "v6\$sub")) { $Missing += "v6\$sub" }
}
if ($Missing.Count -gt 0) {
    Write-Error ("Folder berikut tidak ditemukan di backend\:`n  - " + ($Missing -join "`n  - ") +
                 "`nV6 harus ter-embed di backend\v6\{scripts,skills,templates,checklists}.`n" +
                 "Lihat panduan setup di README.")
    exit 1
}

# Sanity: pastikan binary entrypoint V6 ada
foreach ($script in 'v6\scripts\reviu-rka-kl\run_batch.py', 'v6\scripts\reviu-pengadaan\run_batch.py') {
    if (-not (Test-Path $script)) {
        Write-Warning "Peringatan: $script tidak ditemukan. Skill terkait mungkin tidak jalan."
    }
}

$nScripts = (Get-ChildItem 'v6\scripts' -Directory -ErrorAction SilentlyContinue).Count
$nSkills  = (Get-ChildItem 'v6\skills'  -Directory -ErrorAction SilentlyContinue).Count
Write-Host "[OK] V6 ter-embed: $nScripts item di scripts\, $nSkills item di skills\." -ForegroundColor Green

# === WIKI sync ===
# wiki\ ada di project root, build context Docker = backend\. Sinkronkan ke
# backend\wiki\ supaya bisa di-COPY oleh Dockerfile.
Write-Host ""
Write-Host "Memverifikasi wiki\ di project root..." -ForegroundColor Cyan
$WikiSrc = Join-Path $ProjectRoot 'wiki\temuan-patterns'
if (-not (Test-Path $WikiSrc)) {
    Write-Error ("Folder $WikiSrc tidak ada.`n" +
                 "Wiki diperlukan agen untuk akses pattern temuan. Setup minimal:`n" +
                 "  mkdir wiki\temuan-patterns\reviu-pengadaan, wiki\temuan-patterns\reviu-rka-kl")
    exit 1
}

Write-Host "Sinkron wiki\ -> backend\wiki\ untuk masuk build context..." -ForegroundColor Cyan
if (Test-Path 'wiki') { Remove-Item -Recurse -Force 'wiki' }
New-Item -ItemType Directory -Path 'wiki' | Out-Null
Copy-Item -Recurse (Join-Path $ProjectRoot 'wiki\*') 'wiki\'

$nPbj = (Get-ChildItem 'wiki\temuan-patterns\reviu-pengadaan' -Filter '*.md' -Recurse -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -ne 'README.md' }).Count
$nRka = (Get-ChildItem 'wiki\temuan-patterns\reviu-rka-kl' -Filter '*.md' -Recurse -ErrorAction SilentlyContinue |
         Where-Object { $_.Name -ne 'README.md' }).Count
Write-Host "[OK] Wiki ter-sync: $nPbj pattern reviu-pengadaan, $nRka pattern reviu-rka-kl." -ForegroundColor Green

# Cek apakah app sudah ada di Fly
fly status --app audit-ai-v7 *> $null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Deploying ke app audit-ai-v7 yang sudah ada..." -ForegroundColor Cyan
    fly deploy --app audit-ai-v7
} else {
    Write-Host "App audit-ai-v7 belum ada. Setup pertama kali:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "1) fly launch --copy-config --no-deploy --name audit-ai-v7 --region sin"
    Write-Host "2) fly postgres create --name audit-ai-v7-db --region sin --vm-size shared-cpu-1x"
    Write-Host "3) fly postgres attach audit-ai-v7-db --app audit-ai-v7"
    Write-Host "4) fly volumes create audit_data --app audit-ai-v7 --size 3 --region sin"
    Write-Host "5) fly secrets set ANTHROPIC_API_KEY=sk-ant-... --app audit-ai-v7"
    Write-Host '6) fly secrets set APP_SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))") --app audit-ai-v7'
    Write-Host "7) fly secrets set APP_CORS_ORIGINS=https://audit-ai-v7.vercel.app --app audit-ai-v7"
    Write-Host "8) fly deploy --app audit-ai-v7"
    Write-Host ""
    Write-Host "Setelah deploy pertama berhasil, jalankan script ini lagi untuk redeploy."
}

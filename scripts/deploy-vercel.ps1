# Deployment script untuk Vercel - Windows PowerShell equivalent of deploy-vercel.sh.
#
# Pakai (PowerShell, dari folder audit-system-v7):
#   .\scripts\deploy-vercel.ps1

$ErrorActionPreference = 'Stop'

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $ProjectRoot 'frontend')

if (-not (Get-Command vercel -ErrorAction SilentlyContinue)) {
    Write-Host "Install Vercel CLI..." -ForegroundColor Cyan
    npm install -g vercel
}

Write-Host ""
Write-Host "Sebelum lanjut, pastikan env var sudah di-set di Vercel:" -ForegroundColor Yellow
Write-Host "  NEXT_PUBLIC_API_BASE = https://audit-ai-v7.fly.dev"
Write-Host ""
Write-Host "Atau set di sini:"
Write-Host "  vercel env add NEXT_PUBLIC_API_BASE production"
Write-Host ""

Read-Host "Tekan Enter untuk deploy ke production, atau Ctrl+C untuk batal"

vercel --prod

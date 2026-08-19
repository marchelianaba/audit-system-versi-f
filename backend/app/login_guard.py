"""Proteksi brute-force login (B4) — in-memory, per-username.

Ringan & cukup untuk skala ±80 user dalam 1 proses uvicorn: tak perlu Redis.
Catatan: state hilang saat restart (acceptable — lockout bersifat sementara).
Untuk skala multi-proses/HA nanti, ganti backend ke store bersama (Redis).
"""
from __future__ import annotations

from datetime import datetime, timedelta

from app.config import get_settings

# username (lowercase) -> daftar timestamp kegagalan (UTC)
_failures: dict[str, list[datetime]] = {}
# username (lowercase) -> waktu lockout berakhir (UTC)
_locked_until: dict[str, datetime] = {}


def _key(username: str) -> str:
    return (username or "").strip().lower()


def locked_seconds(username: str) -> int:
    """Sisa detik lockout untuk username, atau 0 bila tidak terkunci."""
    k = _key(username)
    until = _locked_until.get(k)
    if not until:
        return 0
    now = datetime.utcnow()
    if now >= until:
        # lockout sudah lewat → bersihkan
        _locked_until.pop(k, None)
        _failures.pop(k, None)
        return 0
    return int((until - now).total_seconds()) + 1


def record_failure(username: str) -> int:
    """Catat 1 kegagalan login. Return sisa percobaan sebelum terkunci (0 = baru terkunci)."""
    s = get_settings()
    k = _key(username)
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=s.login_attempt_window_minutes)

    recent = [t for t in _failures.get(k, []) if t >= window_start]
    recent.append(now)
    _failures[k] = recent

    if len(recent) >= s.login_max_attempts:
        _locked_until[k] = now + timedelta(minutes=s.login_lockout_minutes)
        return 0
    return s.login_max_attempts - len(recent)


def record_success(username: str) -> None:
    """Reset hitungan setelah login sukses."""
    k = _key(username)
    _failures.pop(k, None)
    _locked_until.pop(k, None)

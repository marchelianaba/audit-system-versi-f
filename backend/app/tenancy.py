"""Isolasi data antar-Inspektorat (I–IV) — satu titik penegakan.

PRINSIP
-------
Penugasan milik satu Inspektorat **tidak boleh terbaca** Inspektorat lain.
Seluruh rute yang menyentuh `Penugasan` WAJIB melewati modul ini, supaya aturan
akses tidak tersebar (dan tidak terlupakan) di belasan berkas rute.

Dua fungsi saja:
  - `filter_penugasan(stmt, user)` → untuk query LIST (menyaring di level SQL)
  - `assert_akses_penugasan(p, user)` → untuk akses satu objek (angkat 404)

KENAPA 404, BUKAN 403
---------------------
403 ("terlarang") mengonfirmasi bahwa penugasan itu ADA. Bagi pengguna
Inspektorat lain, keberadaan sebuah penugasan pun informasi yang tak perlu
diketahui. Maka objek milik Inspektorat lain diperlakukan seolah tidak ada.

DATA LAMA
---------
Baris dengan `inspektorat` NULL (dibuat sebelum fitur ini) di-backfill ke "II"
oleh `init_db.seed_auth`. Bila karena suatu hal masih ada NULL, objek tsb
diperlakukan **tertutup** (hanya bisa diakses pengguna yang juga NULL) — gagal
ke arah aman, bukan terbuka.
"""
from __future__ import annotations

from fastapi import HTTPException, status

from app.models import Penugasan, User

_PESAN_404 = "Penugasan tidak ditemukan"


def inspektorat_user(user: User | None) -> str | None:
    """Kode Inspektorat pengguna (None bila belum diset)."""
    if user is None:
        return None
    v = getattr(user, "inspektorat", None)
    return str(v).strip() if v else None


def filter_penugasan(stmt, user: User | None):
    """Sematkan penyaringan Inspektorat ke SELECT Penugasan (untuk LIST).

    Dipakai bersama `select(Penugasan)`; mengembalikan statement yang sudah
    di-`where`. Menyaring di SQL (bukan setelah fetch) supaya data Inspektorat
    lain tidak pernah masuk ke memori proses.
    """
    ins = inspektorat_user(user)
    if ins is None:
        # Pengguna tanpa inspektorat hanya melihat baris yang juga tanpa inspektorat.
        return stmt.where(Penugasan.inspektorat.is_(None))
    return stmt.where(Penugasan.inspektorat == ins)


def boleh_akses(p: Penugasan | None, user: User | None) -> bool:
    """True bila `user` berhak atas penugasan `p`."""
    if p is None:
        return False
    milik = getattr(p, "inspektorat", None)
    milik = str(milik).strip() if milik else None
    return milik == inspektorat_user(user)


def assert_akses_penugasan(p: Penugasan | None, user: User | None) -> Penugasan:
    """Pastikan `user` berhak atas `p`; bila tidak → 404 (bukan 403).

    Return `p` supaya bisa dipakai sebagai ekspresi:
        p = assert_akses_penugasan(p, user)
    """
    if p is None or not boleh_akses(p, user):
        raise HTTPException(status.HTTP_404_NOT_FOUND, _PESAN_404)
    return p

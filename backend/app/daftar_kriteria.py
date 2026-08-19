"""Daftar Kriteria penugasan — kontrak berkas `_PKP/daftar-kriteria.json`.

LATAR. Skill "umum" (audit/reviu/evaluasi/pemantauan) bersifat *criteria-driven*:
tidak punya kriteria baku bawaan seperti `reviu-rka-kl` (PMK 107/2024) atau
`reviu-pengadaan` (Perpres 16/2018). Kriterianya disediakan auditor per
penugasan. Sebelumnya hal itu hanya berupa dokumen yang diunggah dan berharap
agen menemukan sendiri pasal yang relevan — boros token, sering meleset, dan
tidak ada jaminan kriterianya benar-benar ada.

Berkas ini menjadikannya EKSPLISIT. Dua bentuk entri, keduanya setara sah:

  • UNGGAHAN — berkas kriteria + rujukan bagian yang dipakai (pasal WAJIB;
    halaman wajib hanya bila berkasnya hasil pindai, karena tulisan di gambar
    tak bisa dicari tanpa nomor halaman lebih dulu).
  • KETIK    — kriteria diketik auditor, untuk ketentuan yang tak berdokumen
    digital (SE, kebijakan internal).

Disimpan sebagai BERKAS di folder penugasan, bukan tabel basis data, mengikuti
pola kontrak-berkas sistem ini (`sasaran-assignment.json`, `temuan.json`):
agen membacanya langsung, dan isinya ikut terarsip bersama kertas kerja.

Dipakai oleh:
  - digest (`digest_generic`)  → menentukan halaman mana yang perlu di-OCR
  - gerbang aksi AI            → memastikan kriteria ada sebelum analisis jalan
  - agen                       → tahu pasal apa yang dipakai, tanpa menyapu berkas
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REL_PATH = "_PKP/daftar-kriteria.json"

TIPE_UNGGAHAN = "UNGGAHAN"
TIPE_KETIK = "KETIK"


def path_for(folder: str | Path) -> Path:
    return Path(folder) / "_PKP" / "daftar-kriteria.json"


def read(folder: str | Path) -> dict[str, Any]:
    """Baca daftar kriteria. Selalu mengembalikan bentuk yang aman dipakai.

    Berkas belum ada / rusak → `{"versi": 1, "entri": []}`, bukan galat: daftar
    yang belum diisi adalah keadaan normal di awal penugasan.
    """
    p = path_for(folder)
    if not p.is_file():
        return {"versi": 1, "entri": []}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"versi": 1, "entri": []}
    if not isinstance(data, dict):
        return {"versi": 1, "entri": []}
    entri = data.get("entri")
    data["entri"] = entri if isinstance(entri, list) else []
    data.setdefault("versi", 1)
    return data


def write(folder: str | Path, data: dict[str, Any]) -> None:
    """Tulis daftar kriteria (dipakai endpoint). Membuat `_PKP/` bila perlu."""
    p = path_for(folder)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def entri(folder: str | Path) -> list[dict[str, Any]]:
    return [e for e in read(folder).get("entri", []) if isinstance(e, dict)]


def jumlah(folder: str | Path) -> int:
    return len(entri(folder))


def ada_kriteria(folder: str | Path) -> bool:
    """True bila minimal satu kriteria terisi — dari unggahan ATAU diketik.

    Inilah syarat gerbang aksi AI pada skill umum. Sengaja TIDAK mensyaratkan
    berkas: auditor yang kriterianya berupa SE tanpa lampiran digital tetap bisa
    maju, asalkan menuliskannya.
    """
    for e in entri(folder):
        tipe = str(e.get("tipe") or "").upper()
        if tipe == TIPE_KETIK and str(e.get("teks") or "").strip():
            return True
        if tipe == TIPE_UNGGAHAN and str(e.get("file") or "").strip():
            return True
    return False


_RANGE_RE = re.compile(r"(\d{1,4})\s*(?:[-–—]\s*(\d{1,4}))?")


def parse_halaman(teks: str | None) -> list[int]:
    """Ubah tulisan halaman auditor jadi daftar nomor.

    Menerima bentuk bebas yang lazim ditulis orang: "hal. 14-16", "14, 31",
    "hlm 7". Rentang terbalik/berlebihan diabaikan supaya salah ketik tidak
    berubah jadi perintah meng-OCR ratusan halaman.
    """
    if not teks:
        return []
    out: list[int] = []
    for m in _RANGE_RE.finditer(str(teks)):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if a < 1 or b < a or (b - a) > 50:
            continue
        out.extend(range(a, b + 1))
    # unik, urut, dan dibatasi supaya tidak ada permintaan OCR yang liar
    return sorted(set(out))[:60]


def _norm(nama: str) -> str:
    return Path(str(nama).replace("\\", "/")).name.strip().lower()


def halaman_untuk(folder: str | Path, file_path: str | Path) -> list[int]:
    """Halaman yang DITUNJUK auditor untuk sebuah berkas kriteria.

    Dicocokkan berdasar nama berkas (bukan path penuh) supaya tahan terhadap
    perbedaan penulisan path relatif/absolut antar pemanggil.
    """
    target = _norm(file_path)
    out: list[int] = []
    for e in entri(folder):
        if str(e.get("tipe") or "").upper() != TIPE_UNGGAHAN:
            continue
        if _norm(e.get("file") or e.get("nama_file") or "") != target:
            continue
        for r in e.get("rujukan") or []:
            if isinstance(r, dict):
                out.extend(parse_halaman(r.get("halaman")))
    return sorted(set(out))


def berkas_kriteria(folder: str | Path) -> list[str]:
    """Nama berkas (lowercase) yang terdaftar sebagai kriteria unggahan."""
    return [
        _norm(e.get("file") or e.get("nama_file") or "")
        for e in entri(folder)
        if str(e.get("tipe") or "").upper() == TIPE_UNGGAHAN
        and (e.get("file") or e.get("nama_file"))
    ]


def ringkas(folder: str | Path) -> list[dict[str, Any]]:
    """Bentuk ringkas untuk agen & UI: satu baris per kriteria."""
    out: list[dict[str, Any]] = []
    for e in entri(folder):
        tipe = str(e.get("tipe") or "").upper()
        if tipe == TIPE_KETIK:
            out.append({
                "id": e.get("id") or "",
                "tipe": TIPE_KETIK,
                "sumber": e.get("sumber") or "",
                "teks": str(e.get("teks") or "")[:1500],
            })
        else:
            out.append({
                "id": e.get("id") or "",
                "tipe": TIPE_UNGGAHAN,
                "file": e.get("file") or "",
                "nama_file": e.get("nama_file") or Path(str(e.get("file") or "")).name,
                "pindai": bool(e.get("pindai")),
                "rujukan": [
                    {
                        "pasal": str(r.get("pasal") or "")[:200],
                        "halaman": str(r.get("halaman") or "")[:40],
                    }
                    for r in (e.get("rujukan") or [])
                    if isinstance(r, dict)
                ],
            })
    return out


def id_berikutnya(folder: str | Path) -> str:
    """ID entri berikutnya (K-001, K-002, ...) — pakai MAX+1, bukan len()+1.

    Pola len()+1 pernah membuat temuan lama tertimpa diam-diam setelah ada yang
    dihapus (lihat catatan di ROADMAP-FREE Fase 2B). Jangan diulang di sini.
    """
    tertinggi = 0
    for e in entri(folder):
        m = re.match(r"^K-(\d+)$", str(e.get("id") or ""))
        if m:
            tertinggi = max(tertinggi, int(m.group(1)))
    return f"K-{tertinggi + 1:03d}"

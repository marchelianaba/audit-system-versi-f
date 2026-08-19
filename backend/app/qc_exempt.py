"""Pengecualian QC SAIPI untuk temuan yang ditulis auditor sendiri (manual).

LATAR
-----
Keputusan pemilik proses (9 Agu 2026): temuan ber-`origin="MANUAL"` TIDAK wajib
mencantumkan `dokumen_sumber`. Alasannya, temuan manual diperiksa sendiri oleh
auditor dari hulu ke hilir — "temuan manual, semua manual".

Masalahnya, dua aturan QC SAIPI menuntut hal itu untuk SETIAP temuan:
  - LAK-001 (SAIPI 2310) — setiap temuan punya `dokumen_sumber` minimal 1
  - LAK-003 (SAIPI 2310) — setiap `dokumen_sumber` mencantumkan halaman
Keduanya ber-severity KRITIS, sehingga tanpa penanganan, tiap temuan manual
selalu muncul sebagai pelanggaran kritis.

KENAPA DIKERJAKAN DI SINI, BUKAN DI V6
--------------------------------------
`backend/v6/scripts/qc_saipi.py` berstatus READ-ONLY (invariant proyek: manusia
boleh memperbarui V6, tetapi app-layer tidak menulis ulang logikanya). Jadi QC
tetap dijalankan APA ADANYA atas seluruh temuan; modul ini bekerja SESUDAHNYA,
atas berkas hasil QC.

CARA KERJA — dan kenapa TIDAK mengurai kalimat QC
-------------------------------------------------
Godaan yang jelas adalah membaca `bukti` LAK-001 yang berbunyi
    "2 temuan tanpa dokumen_sumber: ['T-001', 'T-003']"
lalu mengorek nomor temuannya dari kalimat itu. Itu RAPUH: begitu kalimatnya
diperhalus di kemudian hari, pengorekan berhenti mengenali polanya dan gagal
DIAM-DIAM (temuan manual kembali KRITIS tanpa pesan error apa pun).

Karena itu modul ini menilai ULANG secara mandiri dari `_KKP/temuan.json` —
aturannya sederhana dan bisa dihitung sendiri. Satu-satunya yang dipinjam dari
keluaran QC adalah `rule_id` ("LAK-001"/"LAK-003"): kode pendek yang stabil,
bukan prosa.

KEJUJURAN AUDIT
---------------
Pengecualian TIDAK menghapus jejak:
  - entri checklist menyimpan putusan asli V6 di `_asli_v6`
  - blok `_pengecualian_manual` mencatat temuan mana yang dikecualikan
  - laporan markdown diberi bagian tambahan yang menerangkan hal ini
Dan bila ada temuan NON-manual yang juga kosong dokumen sumbernya, statusnya
TETAP KRITIS — pengecualian tidak pernah menutupi kelalaian di jalur AI.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

# Ikon severity — sama dengan render_markdown() di qc_saipi.py, supaya laporan
# yang kita sesuaikan tetap terbaca seragam dengan bagian yang tidak disentuh.
_IKON = {"OK": "✅", "KRITIS": "🔴", "PERINGATAN": "🟡", "NEEDS_REVIEW": "🔵"}

# Aturan yang boleh dikecualikan. Sengaja dibatasi pada dua aturan yang MEMANG
# menegakkan kewajiban dokumen sumber. LAK-002 (berkas yang dirujuk harus ada di
# folder penugasan) TIDAK termasuk: kalau auditor sukarela menyebut nama berkas,
# berkas itu memang sepatutnya ada — menyembunyikan salah ketik di situ tidak
# menolong siapa pun.
RULE_ADA_SUMBER = "LAK-001"
RULE_ADA_HALAMAN = "LAK-003"

_ALASAN = (
    "Dikecualikan: temuan ditulis auditor sendiri (manual) sehingga "
    "pemeriksaannya dilakukan manual oleh auditor, bukan oleh QC otomatis."
)


def _temuan_manual_ids(folder: Path) -> tuple[set[str], set[str], set[str]]:
    """Baca temuan.json → (semua_manual, tanpa_sumber, sumber_tanpa_halaman).

    Perhitungan ini MENIRU logika LAK-001/LAK-003 di qc_saipi.py, dilakukan
    mandiri supaya tidak bergantung pada kalimat laporan QC.
    """
    path = folder / "_KKP" / "temuan.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set(), set(), set()

    manual: set[str] = set()
    tanpa_sumber: set[str] = set()
    tanpa_halaman: set[str] = set()
    for t in (data.get("temuan") or []) if isinstance(data, dict) else []:
        if not isinstance(t, dict):
            continue
        tid = str(t.get("id_temuan") or "").strip()
        if not tid:
            continue
        if str(t.get("origin") or "AI").upper() == "MANUAL":
            manual.add(tid)
        sumber = t.get("dokumen_sumber") or []
        if not sumber:
            tanpa_sumber.add(tid)
            continue
        for d in sumber:
            if isinstance(d, dict) and not d.get("halaman"):
                tanpa_halaman.add(tid)
                break
    return manual, tanpa_sumber, tanpa_halaman


def _sesuaikan_entri(
    entri: dict[str, Any], kena: set[str], manual: set[str]
) -> tuple[dict[str, Any], list[str], list[str]]:
    """Sesuaikan satu entri checklist. Return (entri, dikecualikan, tersisa)."""
    dikecualikan = sorted(kena & manual)
    tersisa = sorted(kena - manual)

    if not dikecualikan:
        return entri, [], tersisa

    # Simpan putusan ASLI V6 sebelum diubah — jejak tidak boleh hilang.
    entri["_asli_v6"] = {
        "status": entri.get("status"),
        "severity": entri.get("severity"),
        "bukti": entri.get("bukti"),
    }
    entri["_dikecualikan_manual"] = dikecualikan

    if tersisa:
        # Masih ada temuan NON-manual yang melanggar → tetap KRITIS. Pengecualian
        # tidak boleh dipakai untuk meloloskan kelalaian di jalur AI.
        entri["bukti"] = (
            f"{len(tersisa)} temuan (non-manual) melanggar: {tersisa}. "
            f"{len(dikecualikan)} temuan manual dikecualikan: {dikecualikan}."
        )
    else:
        entri["status"] = "DIKECUALIKAN"
        entri["severity"] = "OK"
        entri["bukti"] = (
            f"{len(dikecualikan)} temuan manual dikecualikan: {dikecualikan}. {_ALASAN}"
        )
        entri["gap"] = ""
    return entri, dikecualikan, tersisa


def _perbarui_laporan_md(
    md_path: Path,
    disesuaikan: dict[str, dict],
    summary: dict[str, int],
) -> bool:
    """Perbarui laporan markdown QC agar SEJALAN dengan checklist yang disesuaikan.

    Kenapa ini wajib, bukan sekadar menempel catatan di akhir: agen (dan auditor)
    membaca laporan .md, dan `run_qc_*` hanya mengirim 4000 karakter PERTAMA ke
    agen. Pada 13 Agu 2026 terbukti fatal — bagian LAK-001 bertanda 🔴 KRITIS ada
    di karakter ~2800 (terbaca agen) sementara catatan pengecualian di ~8200
    (tidak terbaca). Agen lalu melaporkan ke Ketua Tim bahwa T-003 memblokir LHR,
    padahal checklist sudah menyatakan DIKECUALIKAN. Laporan yang saling
    bertentangan lebih berbahaya daripada tidak ada laporan.

    Return True bila berhasil menulis. Gagal → biarkan berkas apa adanya.
    """
    try:
        teks = md_path.read_text(encoding="utf-8")
    except OSError:
        return False

    keluar: list[str] = []
    rule_aktif: str | None = None
    for baris in teks.splitlines():
        # --- Ringkasan hitungan di kepala laporan ---
        if baris.startswith("- ✅ OK: **"):
            keluar.append(f"- ✅ OK: **{summary['ok']}**")
            continue
        if baris.startswith("- 🔴 KRITIS: **"):
            keluar.append(f"- 🔴 KRITIS: **{summary['kritis']}**")
            continue
        if baris.startswith("- 🟡 PERINGATAN: **"):
            keluar.append(f"- 🟡 PERINGATAN: **{summary['peringatan']}**")
            continue
        if baris.startswith("- 🔵 NEEDS_REVIEW: **"):
            keluar.append(f"- 🔵 NEEDS_REVIEW: **{summary['needs_review']}**")
            continue

        # --- Blok status BLOKIR/PASS ---
        if baris.startswith("## ⛔ Status: BLOKIR"):
            keluar.append(
                "## ⛔ Status: BLOKIR"
                if summary["kritis"] > 0
                else "## ✅ Status: PASS (gap KRITIS tersisa: 0 — sebagian dikecualikan, lihat bagian akhir)"
            )
            continue
        if baris.startswith("Ada **") and "gap KRITIS**" in baris:
            if summary["kritis"] > 0:
                keluar.append(
                    f"Ada **{summary['kritis']} gap KRITIS** yang harus dikoreksi "
                    "sebelum berkas penugasan disubmit ke INTEGRAL."
                )
            # kritis habis → baris ini dibuang, digantikan status PASS di atas
            continue

        # --- Bagian per-aturan ---
        if baris.startswith("### "):
            rule_aktif = None
            for rid, entri in disesuaikan.items():
                if f" {rid} — " in baris:
                    rule_aktif = rid
                    ikon = _IKON.get(entri.get("severity", ""), "◾")
                    baris = re.sub(r"^### \S+ ", f"### {ikon} ", baris)
                    break
            keluar.append(baris)
            continue

        if rule_aktif:
            entri = disesuaikan[rule_aktif]
            if baris.startswith("- **Status**:"):
                keluar.append(f"- **Status**: {entri.get('status')}")
                continue
            if baris.startswith("- **Severity**:"):
                keluar.append(f"- **Severity**: {entri.get('severity')}")
                continue
            if baris.startswith("- **Bukti**:"):
                keluar.append(f"- **Bukti**: {entri.get('bukti')}")
                asli = entri.get("_asli_v6") or {}
                keluar.append(
                    f"- **Putusan asli QC V6**: {asli.get('status')} / "
                    f"{asli.get('severity')} — {asli.get('bukti')}"
                )
                continue
            if baris.startswith("- **Gap / Tindak lanjut**:") and not entri.get("gap"):
                continue

        keluar.append(baris)

    try:
        md_path.write_text("\n".join(keluar), encoding="utf-8")
    except OSError:
        return False
    return True


def _hitung_summary(items: list[dict]) -> dict[str, int]:
    return {
        "ok": sum(1 for i in items if i.get("severity") == "OK"),
        "kritis": sum(1 for i in items if i.get("severity") == "KRITIS"),
        "peringatan": sum(1 for i in items if i.get("severity") == "PERINGATAN"),
        "needs_review": sum(1 for i in items if i.get("severity") == "NEEDS_REVIEW"),
        "not_applicable": sum(1 for i in items if i.get("status") == "NOT_APPLICABLE"),
    }


def terapkan_pengecualian_manual(folder: Path, stage: str) -> dict[str, Any]:
    """Sesuaikan hasil QC SAIPI: kecualikan temuan manual dari LAK-001/LAK-003.

    Dipanggil SETELAH `qc_saipi.py` selesai menulis
    `_QA-SAIPI/checklist-{stage}.json`. Best-effort: bila apa pun gagal dibaca,
    hasil QC dibiarkan apa adanya (lebih baik KRITIS palsu daripada PASS palsu).

    Return ringkasan: {"diterapkan": bool, "dikecualikan": [...], "tersisa": [...]}.
    """
    hasil: dict[str, Any] = {"diterapkan": False, "dikecualikan": [], "tersisa": []}

    manual, tanpa_sumber, tanpa_halaman = _temuan_manual_ids(folder)
    if not manual:
        return hasil  # tak ada temuan manual → tak ada yang perlu disesuaikan

    ck_path = folder / "_QA-SAIPI" / f"checklist-{stage}.json"
    try:
        payload = json.loads(ck_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return hasil
    if not isinstance(payload, dict) or not isinstance(payload.get("checklist"), list):
        return hasil

    semua_dikecualikan: set[str] = set()
    semua_tersisa: set[str] = set()
    disesuaikan: dict[str, dict] = {}

    for entri in payload["checklist"]:
        if not isinstance(entri, dict) or entri.get("status") != "GAP":
            continue
        rid = entri.get("rule_id")
        if rid == RULE_ADA_SUMBER:
            kena = tanpa_sumber
        elif rid == RULE_ADA_HALAMAN:
            kena = tanpa_halaman
        else:
            continue
        _, dikecualikan, tersisa = _sesuaikan_entri(entri, kena, manual)
        if dikecualikan:
            disesuaikan[str(rid)] = entri
            semua_dikecualikan.update(dikecualikan)
            semua_tersisa.update(tersisa)

    if not disesuaikan:
        return hasil

    payload["summary"] = _hitung_summary(payload["checklist"])
    payload["_pengecualian_manual"] = {
        "alasan": _ALASAN,
        "aturan": [RULE_ADA_SUMBER, RULE_ADA_HALAMAN],
        "temuan_dikecualikan": sorted(semua_dikecualikan),
        "catatan": (
            "Putusan asli V6 disimpan di field `_asli_v6` pada tiap entri "
            "checklist yang disesuaikan."
        ),
    }
    try:
        ck_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except OSError:
        return hasil

    # Laporan .md WAJIB ikut disesuaikan di tempatnya — bukan cuma ditempeli
    # catatan di akhir. Auditor & agen membaca .md, dan agen hanya menerima 4000
    # karakter pertamanya; catatan di ekor tidak akan pernah terbaca sementara
    # bagian 🔴 KRITIS di badan laporan terbaca. Lihat _perbarui_laporan_md.
    md_path = folder / "_QA-SAIPI" / f"laporan-qa-{stage}.md"
    if md_path.is_file():
        _perbarui_laporan_md(md_path, disesuaikan, payload["summary"])
        try:
            catatan = (
                "\n\n---\n\n## Pengecualian Temuan Manual\n\n"
                f"{_ALASAN}\n\n"
                f"- Aturan yang dikecualikan: **{RULE_ADA_SUMBER}**, **{RULE_ADA_HALAMAN}**\n"
                f"- Temuan yang dikecualikan: {', '.join(sorted(semua_dikecualikan))}\n"
            )
            if semua_tersisa:
                catatan += (
                    f"- **Tetap KRITIS** (bukan temuan manual, wajib diperbaiki): "
                    f"{', '.join(sorted(semua_tersisa))}\n"
                )
            catatan += (
                "\n> Putusan asli QC V6 tidak dihapus — tersimpan di badan laporan "
                f"(baris \"Putusan asli QC V6\") dan di `checklist-{stage}.json` "
                "pada field `_asli_v6`.\n"
            )
            md_path.write_text(
                md_path.read_text(encoding="utf-8") + catatan, encoding="utf-8"
            )
        except OSError:
            pass  # laporan .md gagal ditulis → checklist JSON tetap benar

    hasil["diterapkan"] = True
    hasil["dikecualikan"] = sorted(semua_dikecualikan)
    hasil["tersisa"] = sorted(semua_tersisa)
    return hasil

"""Penyusun LHR gaya NARASI — meniru format baku laporan Inspektorat II.

KENAPA MODUL BARU, BUKAN MENGUBAH YANG ADA
------------------------------------------
Jalur lama (`render_report` → V6 `render_lhp.py`) TIDAK disentuh sama sekali.
Modul ini berdiri sendiri dan menulis berkas dengan nama berbeda
(`LHR-NARASI-*.docx`), sehingga:
  - laporan lama tetap bisa dibuat seperti biasa,
  - kalau hasil gaya baru ini dinilai jelek, cukup berhenti memakainya —
    tidak ada yang perlu dikembalikan.

DASAR FORMAT
------------
Disusun dari empat laporan asli buatan auditor Inspektorat II (dipelajari
13 Agu 2026):
  - Reviu Pengadaan Perpanjangan Lisensi Firewall PSrE Induk
  - Revisi LHR Dokumen Pengadaan Pusat Data & DRC PSrE Induk (B-93/2026)
  - LHR Pengadaan Paket Pembelian & Jasa Konsultansi Ditdal Ekosdig (B-164/2026)
  - LHR Rencana Pengadaan Dukungan Teknis & CNS TKPPSE (B-227/2026)

Kerangka bab yang konsisten di keempatnya:
  A. Dasar Pelaksanaan Reviu       E. Gambaran Umum (+ tabel harga)
  B. Tujuan dan Sasaran Reviu      F. Hasil Reviu
  C. Ruang Lingkup Reviu           G. Hal-hal yang Harus diperhatikan (opsional)
  D. Metodologi Reviu              H. Apresiasi

PERBEDAAN POKOK DARI FORMAT LAMA
--------------------------------
1. Temuan ditulis sebagai NARASI MENGALIR — tanpa label Kondisi/Kriteria/
   Sebab/Akibat. Narasinya disusun agen Ketua Tim (lihat `write_narasi_laporan`),
   BUKAN disambung mekanis dari potongan `temuan.json`. Kertas kerja AT tetap utuh.
2. TIDAK ada bab Simpulan & Rekomendasi terpisah. Kalimat keyakinan menempel
   di akhir bab Hasil Reviu.
3. Tiap catatan diakhiri placeholder tanggapan Satker — diisi auditor manual
   setelah Satker menjawab (keputusan pemilik proses 13 Agu 2026).
4. Kalimat keyakinan memakai bentuk "KECUALI" bila masih ada catatan terbuka;
   bentuk penuh hanya dipakai bila tidak ada catatan sama sekali. Tanpa ini
   laporan bisa menyatakan "semua sesuai" sambil mendaftar 6 masalah.

Khusus skill `reviu-pengadaan`. Skill lain tidak terpengaruh.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt

FONT = "Arial"

# Kalimat-kalimat baku — disalin PERSIS dari laporan asli. Jangan "diperbaiki"
# gayanya: keseragaman antar-laporan adalah ciri format resmi ini.
RUANG_LINGKUP_BAKU = (
    "Ruang lingkup reviu adalah penelaahan atas seluruh data dukung yang "
    "dilakukan secara terbatas serta tidak mencakup pengujian atas sistem "
    "pengendalian intern dan pengujian atas respon permintaan keterangan yang "
    "biasanya dilaksanakan dalam suatu audit."
)
METODOLOGI_BAKU = (
    "Reviu dilaksanakan dengan melakukan penelaahan atas seluruh data dukung "
    "serta melakukan konfirmasi dengan petugas/pejabat yang terkait."
)
PLACEHOLDER_TANGGAPAN = (
    "[DIISI AUDITOR — tanggapan dan tindak lanjut Satker, serta hasil "
    "verifikasi tim reviu]"
)
PENUTUP = (
    "Terima kasih telah membantu kami dalam menjaga integritas. Demikian "
    "laporan ini kami sampaikan. Atas perhatian dan kerja sama Bapak/Ibu kami "
    "ucapkan terima kasih."
)


# ── util dokumen ─────────────────────────────────────────────────────────────

def _p(doc: Document, teks: str, *, bold=False, size=12, align="justify",
       indent: float | None = None, space_after=6) -> Any:
    par = doc.add_paragraph()
    par.paragraph_format.space_after = Pt(space_after)
    if indent is not None:
        par.paragraph_format.left_indent = Cm(indent)
    par.alignment = {
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
    }.get(align, WD_ALIGN_PARAGRAPH.JUSTIFY)
    run = par.add_run(teks)
    run.bold = bold
    run.font.name = FONT
    run.font.size = Pt(size)
    return par


def _bab(doc: Document, huruf: str, judul: str) -> None:
    _p(doc, f"{huruf}. {judul}", bold=True, align="left", space_after=4)


def _judul_reviu(args: dict) -> str:
    """Judul yang selalu diawali kata 'Reviu' — untuk kalimat Surat Tugas.

    Agen lazimnya mengirim judul berupa nama obyek ("Pengadaan Perpanjangan
    Lisensi ..."). Tanpa penyesuaian ini kalimatnya menjadi "Melakukan
    Pengadaan ..." — seolah Inspektorat yang mengadakan, bukan mereviu.
    """
    j = (args.get("judul") or "reviu").strip()
    return j if j.lower().startswith("reviu") else f"Reviu {j}"


# ── pembacaan sumber ─────────────────────────────────────────────────────────

def _baca_json(p: Path) -> dict:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _parse_context(p: Path) -> dict[str, str]:
    """Ambil field dari context.md (format '- **Key**: Value' dan 'Key: Value')."""
    out: dict[str, str] = {}
    try:
        teks = p.read_text(encoding="utf-8")
    except OSError:
        return out
    peta = {
        "obyek": "obyek", "nomor st": "nomor_st", "tanggal st": "tanggal_st",
        "dasar pengawasan": "dasar", "dasar penugasan": "dasar",
        "tahun anggaran": "tahun_anggaran",
    }
    for baris in teks.splitlines():
        b = baris.strip().lstrip("-").strip()
        m = re.match(r"\*\*(.+?)\*\*\s*:\s*(.+)", b) or re.match(r"([A-Za-z /]+)\s*:\s*(.+)", b)
        if not m:
            continue
        kunci, nilai = m.group(1).strip().lower(), m.group(2).strip()
        for pola, target in peta.items():
            if pola in kunci and not out.get(target):
                out[target] = nilai
        if kunci.startswith("tujuan") and not out.get("tujuan"):
            out["tujuan"] = nilai
        if kunci.startswith("ruang lingkup") and not out.get("ruang_lingkup"):
            out["ruang_lingkup"] = nilai
    return out


def _terbilang_sederhana(n: int) -> str:
    kata = ["nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh",
            "delapan", "sembilan", "sepuluh", "sebelas", "dua belas",
            "tiga belas", "empat belas", "lima belas", "enam belas",
            "tujuh belas", "delapan belas", "sembilan belas", "dua puluh"]
    return kata[n] if 0 <= n < len(kata) else str(n)


# ── penyusun bab ─────────────────────────────────────────────────────────────

def _bab_dasar(doc: Document, ctx: dict, args: dict) -> None:
    _bab(doc, "A", "Dasar Pelaksanaan Reviu")
    dasar = (args.get("dasar_permintaan") or ctx.get("dasar") or "").strip()
    butir = []
    if dasar:
        butir.append(dasar if dasar.endswith(".") else dasar + ".")
    st_no = (ctx.get("nomor_st") or "").strip()
    st_tgl = (ctx.get("tanggal_st") or "").strip()
    if st_no:
        # Laporan asli berbunyi "... tentang Melakukan Reviu <obyek>". Judul yang
        # dikirim agen biasanya sudah berupa nama obyek tanpa kata "Reviu", jadi
        # kata itu ditambahkan di sini — kalau tidak, kalimatnya jadi
        # "Melakukan Pengadaan ..." yang justru membalik makna.
        butir.append(
            f"Surat Tugas Inspektur II Nomor {st_no}"
            + (f" tanggal {st_tgl}" if st_tgl else "")
            + f" tentang Melakukan {_judul_reviu(args)}."
        )
    if not butir:
        butir = ["[DIISI AUDITOR — dasar pelaksanaan reviu]"]
    for i, b in enumerate(butir, 1):
        _p(doc, f"{i}. {b}", indent=0.75)


def _bab_tujuan(doc: Document, ctx: dict, sasaran: list[dict], args: dict) -> None:
    _bab(doc, "B", "Tujuan dan Sasaran Reviu")
    tujuan = (args.get("tujuan") or ctx.get("tujuan") or "").strip()
    if not tujuan:
        tujuan = (
            f"memberikan keyakinan terbatas atas {args.get('judul') or '[DIISI AUDITOR]'}"
        )
    # Samakan gaya laporan asli: "Tujuan dari dilaksanakannya reviu adalah untuk ..."
    if not tujuan.lower().startswith("tujuan"):
        tujuan_kal = f"Tujuan dari dilaksanakannya reviu adalah untuk {tujuan[0].lower() + tujuan[1:]}"
    else:
        tujuan_kal = tujuan
    _p(doc, f"a. {tujuan_kal}", indent=0.75)
    _p(doc, "b. Sasaran dari dilaksanakannya reviu adalah untuk:", indent=0.75)
    if sasaran:
        for i, s in enumerate(sasaran, 1):
            d = (s.get("deskripsi") or s.get("sasaran_id") or "").strip()
            if d and not d.endswith((".", ";")):
                d += "."
            _p(doc, f"{i}. {d}", indent=1.5)
    else:
        _p(doc, "1. [DIISI AUDITOR — sasaran reviu]", indent=1.5)


def _bab_gambaran(doc: Document, args: dict, komponen: list[dict]) -> None:
    _bab(doc, "E", "Gambaran Umum")
    gu = (args.get("gambaran_umum") or "").strip()
    _p(doc, gu or "[DIISI AUDITOR — gambaran umum pengadaan]")
    if not komponen:
        return
    _p(doc, "Berikut adalah rincian komponen dan harga yang akan diadakan:",
       space_after=4)
    tab = doc.add_table(rows=1, cols=5)
    tab.style = "Table Grid"
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, judul in enumerate(["No", "Nama Pengadaan", "Jumlah", "Satuan", "Nominal"]):
        sel = tab.rows[0].cells[i]
        sel.text = ""
        r = sel.paragraphs[0].add_run(judul)
        r.bold = True
        r.font.name = FONT
        r.font.size = Pt(11)
    total = 0
    for i, k in enumerate(komponen, 1):
        baris = tab.add_row().cells
        nilai = k.get("nominal")
        try:
            total += int(str(nilai).replace(".", "").replace(",", "").replace("Rp", "").strip())
        except (TypeError, ValueError):
            pass
        for j, v in enumerate([str(i), k.get("nama", ""), str(k.get("jumlah", "")),
                               k.get("satuan", ""), _rupiah(nilai)]):
            baris[j].text = ""
            r = baris[j].paragraphs[0].add_run(v)
            r.font.name = FONT
            r.font.size = Pt(11)
    baris = tab.add_row().cells
    baris[0].merge(baris[3])
    for sel, v, tebal in ((baris[0], "TOTAL NOMINAL", True), (baris[4], _rupiah(total), True)):
        sel.text = ""
        r = sel.paragraphs[0].add_run(v)
        r.bold = tebal
        r.font.name = FONT
        r.font.size = Pt(11)
    doc.add_paragraph()


def _rupiah(v: Any) -> str:
    if v in (None, ""):
        return ""
    s = str(v)
    if s.strip().lower().startswith("rp"):
        return s
    try:
        return "Rp" + f"{int(str(v).replace('.', '').replace(',', '').strip()):,}".replace(",", ".")
    except (TypeError, ValueError):
        return s


def _bab_hasil(doc: Document, catatan: list[dict], args: dict, ada_catatan: bool) -> None:
    _bab(doc, "F", "Hasil Reviu")
    obyek = args.get("judul") or "pengadaan"
    if ada_catatan:
        n = len(catatan)
        _p(doc,
           f"Berdasarkan hasil reviu atas {obyek}, tim reviu menyampaikan "
           f"{n} ({_terbilang_sederhana(n)}) catatan sebagaimana diuraikan "
           f"berikut ini.")
    else:
        _p(doc, f"Berdasarkan hasil reviu atas {obyek}, didapatkan hasil sebagai berikut:")

    for i, c in enumerate(catatan, 1):
        judul = (c.get("judul") or "").strip() or f"Catatan {i}"
        _p(doc, f"{i}. {judul}", bold=True, align="left", indent=0.75, space_after=4)
        narasi = (c.get("narasi") or "").strip()
        for blok in [x for x in narasi.split("\n") if x.strip()]:
            _p(doc, blok.strip(), indent=0.75)
        # Placeholder tanggapan HANYA untuk catatan (bukan pernyataan positif).
        if c.get("jenis", "catatan") == "catatan":
            _p(doc, PLACEHOLDER_TANGGAPAN, indent=0.75)

    # Kalimat keyakinan — bentuk "kecuali" bila masih ada catatan terbuka.
    if ada_catatan:
        kal = (
            f"Berdasarkan hasil reviu, tidak terdapat hal-hal yang membuat kami "
            f"yakin bahwa {obyek} tidak sesuai dengan ketentuan pengadaan "
            f"barang/jasa, kecuali hal-hal yang kami ungkapkan pada bagian "
            f"Hasil Reviu di atas."
        )
    else:
        kal = (
            f"Berdasarkan hasil reviu, tidak terdapat hal-hal yang membuat kami "
            f"yakin bahwa {obyek} tidak sesuai dengan ketentuan pengadaan "
            f"barang/jasa."
        )
    _p(doc, kal)


def _bab_perhatian(doc: Document, butir: list[dict]) -> str:
    if not butir:
        return "F"
    _bab(doc, "G", "Hal-hal yang Harus diperhatikan")
    for i, b in enumerate(butir, 1):
        judul = (b.get("judul") or "").strip()
        if judul:
            _p(doc, f"{i}. {judul}", bold=True, align="left", indent=0.75, space_after=4)
        _p(doc, (b.get("uraian") or "").strip(), indent=0.75)
    return "G"


def _bab_apresiasi(doc: Document, huruf: str, auditi: str) -> None:
    _bab(doc, huruf, "Apresiasi")
    _p(doc,
       f"Inspektorat II menyampaikan terima kasih kepada seluruh pejabat/pegawai "
       f"di lingkungan {auditi} atas bantuan dan kerja samanya dalam mendukung "
       f"terlaksananya reviu ini.")
    doc.add_paragraph()
    _p(doc, PENUTUP)
    doc.add_paragraph()
    _p(doc, "Inspektur II,", align="left", space_after=0)
    doc.add_paragraph()
    doc.add_paragraph()
    _p(doc, "${ttd_pengirim}", align="left", space_after=0)


# ── titik masuk ──────────────────────────────────────────────────────────────

def render(folder: Path, args: dict) -> tuple[bool, str, Path | None]:
    """Bangun LHR gaya narasi. Return (berhasil, pesan, path)."""
    ctx = _parse_context(folder / "context.md")
    sa = _baca_json(folder / "_PKP" / "sasaran-assignment.json")
    sasaran = sa.get("sasaran", []) if isinstance(sa, dict) else []
    narasi_doc = _baca_json(folder / "_LHP" / "narasi-laporan.json")

    catatan = narasi_doc.get("catatan") or []
    if not isinstance(catatan, list) or not catatan:
        return (False,
                "narasi-laporan.json belum ada / kosong — panggil "
                "write_narasi_laporan lebih dulu untuk menyusun narasi tiap catatan.",
                None)

    ada_catatan = any(c.get("jenis", "catatan") == "catatan" for c in catatan)
    auditi = (args.get("auditi") or "[DIISI AUDITOR]").strip()

    doc = Document()
    st = doc.sections[0]
    st.left_margin, st.right_margin = Cm(3.0), Cm(2.5)
    st.top_margin, st.bottom_margin = Cm(2.5), Cm(2.5)
    normal = doc.styles["Normal"]
    normal.font.name = FONT
    normal.font.size = Pt(12)

    # Kop
    for baris in ("KEMENTERIAN KOMUNIKASI DAN DIGITAL RI",
                  "INSPEKTORAT JENDERAL", "INSPEKTORAT II"):
        _p(doc, baris, bold=True, align="center", space_after=0)
    doc.add_paragraph()
    _p(doc, "LAPORAN HASIL REVIU", bold=True, align="center", space_after=0)
    _p(doc, (args.get("judul") or "[DIISI AUDITOR]").upper(), bold=True,
       align="center", space_after=4)
    _p(doc, "Nomor : B-[DIISI AUDITOR]", align="center", space_after=0)
    _p(doc, "Tanggal : [DIISI AUDITOR]", align="center")
    doc.add_paragraph()

    _p(doc, "Kepada Yth.", align="left", space_after=0)
    _p(doc, auditi, align="left", space_after=0)
    _p(doc, "di Jakarta", align="left")
    doc.add_paragraph()

    dasar = (args.get("dasar_permintaan") or ctx.get("dasar") or "").strip()
    if dasar:
        _p(doc, f"Menindaklanjuti {dasar}, kami telah menerbitkan Surat Tugas "
                f"Nomor {ctx.get('nomor_st', '[DIISI AUDITOR]')} untuk melakukan "
                f"reviu tersebut. Bersama ini kami sampaikan "
                f"{args.get('judul') or 'laporan hasil reviu'}.")
    doc.add_paragraph()

    _bab_dasar(doc, ctx, args)
    doc.add_paragraph()
    _bab_tujuan(doc, ctx, sasaran, args)
    doc.add_paragraph()
    _bab(doc, "C", "Ruang Lingkup Reviu")
    _p(doc, args.get("ruang_lingkup") or RUANG_LINGKUP_BAKU)
    doc.add_paragraph()
    _bab(doc, "D", "Metodologi Reviu")
    _p(doc, args.get("metodologi") or METODOLOGI_BAKU)
    doc.add_paragraph()
    _bab_gambaran(doc, args, narasi_doc.get("komponen_harga") or [])
    _bab_hasil(doc, catatan, args, ada_catatan)
    doc.add_paragraph()
    huruf_akhir = _bab_perhatian(doc, narasi_doc.get("hal_diperhatikan") or [])
    doc.add_paragraph()
    _bab_apresiasi(doc, "H" if huruf_akhir == "G" else "G", auditi)

    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(ctx.get("nomor_st") or "DRAFT")).strip("-")
    out = folder / "_LHP" / f"LHR-NARASI-{slug}.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(out))
    return True, f"{len(catatan)} catatan, gaya narasi", out

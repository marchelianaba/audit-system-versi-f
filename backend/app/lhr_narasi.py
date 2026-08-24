"""Penyusun LHR gaya NARASI untuk `reviu-pengadaan` — dituang ke TEMPLATE resmi.

ISI vs BENTUK
-------------
Dua hal ini dipisah dan tidak boleh tertukar:

  - **Isi** = narasi mengalir per catatan (tanpa label Kondisi/Kriteria/Sebab/
    Akibat). Disusun agen Ketua Tim lewat `write_narasi_laporan`. Kertas kerja
    Anggota Tim tidak disentuh.
  - **Bentuk** = template resmi `template-lhp-reviu-pengadaan.docx` — kop,
    Nota Dinas, halaman cover, surat pengantar, penomoran bab, blok tanda
    tangan. Sama persis dengan lima skill lain.

RIWAYAT (kenapa berubah, 23 Agu 2026)
-------------------------------------
Versi pertama modul ini (13 Agu 2026) membangun dokumen dari NOL dengan
python-docx, memakai kerangka bab A–H yang disarikan dari empat laporan asli
Inspektorat II. Hasilnya benar isinya, tapi **kehilangan Nota Dinas dan halaman
cover** — sehingga tampak berbeda sendiri dibanding laporan skill lain.

Sekarang isinya tetap narasi, tapi dituang ke template. Kerangka babnya
karenanya mengikuti template: A Pendahuluan (dengan sub-butir) · B Gambaran
Umum · C Hasil Reviu · D Simpulan · E Rekomendasi.

Sub-bab C.1 Perencanaan / C.2 Pemilihan **dihapus dari template** (keputusan
pengguna 23 Agu 2026): narasi disusun mengalir per catatan tanpa dipilah tahap,
sehingga salah satu sub-bab selalu kosong. Kini satu penanda `{{C_HASIL_REVIU}}`.

Pemetaan isi lama → bab template:
    kalimat keyakinan   → D. Simpulan      (dulu menempel di akhir Hasil Reviu)
    hal_diperhatikan    → E. Rekomendasi   (dulu bab G tersendiri)
    apresiasi + penutup → sudah ada tetap di template

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
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
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


# ── blok: satuan isi yang nanti ditanam ke penanda template ──────────────────
#
# Bentuk blok:
#   ("p", teks, {bold, italic, align, indent, size})
#   ("tabel", [judul_kolom...], [[sel...], ...])

def P(teks: str, **fmt) -> tuple:
    return ("p", teks, fmt)


def _terapkan_format(par, fmt: dict) -> None:
    par.alignment = {
        "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
    }.get(fmt.get("align", "justify"), WD_ALIGN_PARAGRAPH.JUSTIFY)
    if fmt.get("indent"):
        par.paragraph_format.left_indent = Cm(fmt["indent"])
    # Jorok gantung: baris ke-2 dst sejajar dengan teks SETELAH nomor, bukan
    # menempel ke angkanya. Tanpa ini judul catatan yang panjang terlihat
    # patah dan tidak rata.
    if fmt.get("gantung"):
        par.paragraph_format.first_line_indent = Cm(-fmt["gantung"])
    par.paragraph_format.space_after = Pt(fmt.get("space_after", 6))
    # Spasi 1,5 lewat XML — cara paling andal lintas versi python-docx, sama
    # dengan yang dipakai renderer V6 supaya tampilannya seragam.
    pPr = par._element.get_or_add_pPr()
    sp = OxmlElement("w:spacing")
    sp.set(qn("w:line"), "360")
    sp.set(qn("w:lineRule"), "auto")
    pPr.append(sp)


def _buat_paragraf(doc: Document, teks: str, fmt: dict):
    par = doc.add_paragraph()
    _terapkan_format(par, fmt)
    run = par.add_run(teks)
    run.bold = fmt.get("bold", False)
    run.italic = fmt.get("italic", False)
    run.font.name = FONT
    run.font.size = Pt(fmt.get("size", 12))
    return par


def _buat_tabel(doc: Document, judul_kolom: list[str], baris: list[list[str]],
                opsi: dict | None = None):
    """Tabel ber-garis. `opsi` boleh memuat:

    - `lebar`  : list lebar kolom dalam cm. WAJIB diisi bila tidak ingin Word
                 membagi kolom rata — pembagian rata membuat kolom "No"
                 kelebaran sementara kolom nama terpotong ke dua baris.
    - `gabung_akhir` : jumlah sel pertama pada BARIS TERAKHIR yang digabung
                 (untuk baris TOTAL). Tanpa ini tulisan "TOTAL NOMINAL" nyempil
                 di kolom Nama dan ikut terpotong.
    - `rata_kanan`   : indeks kolom yang isinya dirata-kanankan (kolom nominal).
    """
    opsi = opsi or {}
    lebar = opsi.get("lebar")
    rata_kanan = set(opsi.get("rata_kanan") or [])

    tab = doc.add_table(rows=1, cols=len(judul_kolom))
    tab.style = "Table Grid"
    tab.alignment = WD_TABLE_ALIGNMENT.CENTER
    tab.autofit = False

    def tulis(sel, teks, *, tebal=False, kanan=False):
        sel.text = ""
        par = sel.paragraphs[0]
        if kanan:
            par.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = par.add_run(str(teks))
        r.bold = tebal
        r.font.name = FONT
        r.font.size = Pt(11)

    for i, j in enumerate(judul_kolom):
        tulis(tab.rows[0].cells[i], j, tebal=True)

    n_akhir = len(baris) - 1
    for n, data in enumerate(baris):
        sel_baris = tab.add_row().cells
        gabung = opsi.get("gabung_akhir") if n == n_akhir else None
        if gabung and gabung >= 2:
            digabung = sel_baris[0]
            for k in range(1, gabung):
                digabung = digabung.merge(sel_baris[k])
            tulis(digabung, data[1] or data[0], tebal=True)
            for i in range(gabung, len(data)):
                tulis(sel_baris[i], data[i], tebal=True, kanan=i in rata_kanan)
            continue
        for i, v in enumerate(data):
            tulis(sel_baris[i], v, kanan=i in rata_kanan)

    if lebar:
        # Lebar harus dipasang di SETIAP sel — Word mengabaikan lebar kolom
        # bila sel-selnya sendiri tidak diberi ukuran.
        for row in tab.rows:
            for i, sel in enumerate(row.cells):
                if i < len(lebar):
                    sel.width = Cm(lebar[i])
    return tab


def isi_penanda(doc: Document, peta: dict[str, str]) -> None:
    """Ganti penanda sederhana `{{KUNCI}}` di paragraf dan sel tabel.

    Penanda kerap terpecah antar-run (Word memecah teks saat diedit), jadi
    teks paragraf disatukan dulu sebelum diganti — persis pola renderer V6.
    """
    def ganti(par) -> None:
        penuh = "".join(r.text for r in par.runs)
        if "{{" not in penuh:
            return
        baru = penuh
        for k, v in peta.items():
            baru = baru.replace("{{" + k + "}}", str(v))
        if baru == penuh or not par.runs:
            return
        par.runs[0].text = baru
        for r in par.runs[1:]:
            r.text = ""

    for par in doc.paragraphs:
        ganti(par)
    for tab in doc.tables:
        for row in tab.rows:
            for sel in row.cells:
                for par in sel.paragraphs:
                    ganti(par)


def tanam_blok(doc: Document, penanda: str, blok: list[tuple]) -> int:
    """Ganti paragraf yang memuat `penanda` dengan rangkaian blok.

    Mendukung paragraf DAN tabel — berbeda dari pembantu V6 yang hanya bisa
    paragraf. Dibutuhkan karena bab Gambaran Umum memuat tabel komponen harga.
    """
    sasaran = [p for p in doc.paragraphs if penanda in p.text]
    if not sasaran:
        return 0
    jumlah = 0
    for target in sasaran:
        el = target._element
        for item in blok:
            if item[0] == "p":
                baru = _buat_paragraf(doc, item[1], item[2])
                el.addprevious(baru._element)
            elif item[0] == "tabel":
                tab = _buat_tabel(doc, item[1], item[2],
                                  item[3] if len(item) > 3 else None)
                el.addprevious(tab._element)
                kosong = doc.add_paragraph()
                el.addprevious(kosong._element)
        el.getparent().remove(el)
        jumlah += 1
    return jumlah


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


def _parse_context(p: Path) -> dict[str, Any]:
    """Ambil field dari context.md — bentuk daftar '- Key: Value' maupun tabel."""
    out: dict[str, Any] = {}
    try:
        teks = p.read_text(encoding="utf-8")
    except OSError:
        return out
    peta = {
        "obyek": "obyek", "objek": "obyek",
        "nomor st": "nomor_st", "tanggal st": "tanggal_st",
        "dasar pengawasan": "dasar", "dasar penugasan": "dasar",
        "tahun anggaran": "tahun_anggaran",
        # Agen menulis "- Periode: ..." (bukan "Periode Pelaksanaan"), jadi kunci
        # pendeknya HARUS ikut dikenali. Pola panjang ditaruh lebih dulu agar
        # tetap menang bila keduanya ada.
        "periode pelaksanaan": "periode", "jangka waktu": "periode",
        "periode": "periode",
        "penerima lhp": "penerima_lhp",
    }

    def catat(kunci: str, nilai: str) -> None:
        kunci = kunci.strip().lower()
        nilai = nilai.strip()
        if not nilai:
            return
        for pola, target in peta.items():
            if pola in kunci and not out.get(target):
                out[target] = nilai
                return
        if kunci.startswith("tujuan") and not out.get("tujuan"):
            out["tujuan"] = nilai
        if kunci.startswith("ruang lingkup") and not out.get("ruang_lingkup"):
            out["ruang_lingkup"] = nilai

    for baris in teks.splitlines():
        b = baris.strip()
        if b.startswith("|"):
            sel = [c.strip() for c in b.split("|") if c.strip()]
            if len(sel) >= 2 and not sel[0].startswith("-"):
                catat(sel[0], sel[1])
            continue
        b = b.lstrip("-").strip()
        m = re.match(r"\*\*(.+?)\*\*\s*:\s*(.+)", b) or re.match(r"([A-Za-z /]+)\s*:\s*(.+)", b)
        if m:
            catat(m.group(1), m.group(2))

    # Ringkasan obyek. Nama headingnya berbeda-beda antar penulis context.md —
    # scaffold memakai "Ringkasan Obyek", agen menulis "Gambaran Umum Obyek".
    # Keduanya (dan variannya) harus dikenali, kalau tidak bab Latar Belakang
    # terbit kosong tanpa ada yang sadar.
    for pola in (r"##\s*Gambaran Umum Obyek\s*\n+([\s\S]+?)(?=\n##|\Z)",
                 r"##\s*Ringkasan Obyek\s*\n+([\s\S]+?)(?=\n##|\Z)",
                 r"##\s*Gambaran Umum\s*\n+([\s\S]+?)(?=\n##|\Z)"):
        m = re.search(pola, teks, re.IGNORECASE)
        if m and m.group(1).strip():
            out["ringkasan_obyek"] = m.group(1).strip()
            break

    # Tabel Tim — untuk bab A.7 Komposisi Tim.
    #
    # Dibaca menurut NAMA KOLOM, bukan posisi. Versi sebelumnya mensyaratkan
    # kolom pertama berupa ANGKA, padahal agen menulis tabel berkolom
    # "Peran | Nama Lengkap | NIP | Jabfung" — akibatnya seluruh tim terbaca
    # nol dan bab Komposisi Tim terbit kosong.
    tim: list[dict] = []
    judul_kolom: list[str] = []
    di_tim = False
    for baris in teks.splitlines():
        b = baris.strip()
        if b.lower().startswith("## tim"):
            di_tim = True
            judul_kolom = []
            continue
        if not di_tim:
            continue
        if not b.startswith("|"):
            if b:  # baris bukan-tabel menutup bagian Tim
                di_tim = False
            continue
        sel = [c.strip() for c in b.strip("|").split("|")]
        if all(set(c) <= set("-: ") for c in sel):  # garis pemisah tabel
            continue
        if not judul_kolom:
            judul_kolom = [c.lower() for c in sel]
            continue
        data = dict(zip(judul_kolom, sel))

        def ambil(*kunci: str) -> str:
            for k in kunci:
                for kol, nilai in data.items():
                    if k in kol:
                        return nilai
            return ""

        nama = ambil("nama")
        if not nama:
            continue
        tim.append({
            "no": str(len(tim) + 1),
            "nama": nama,
            "nip": ambil("nip"),
            # Kolom template = "Kedudukan dalam Tim": pakai Peran bila ada,
            # kalau tidak baru jabatan fungsional.
            "jabatan": ambil("peran", "kedudukan", "jabatan") or ambil("jabfung"),
        })
    out["tim"] = tim
    return out


def _terbilang_sederhana(n: int) -> str:
    kata = ["nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh",
            "delapan", "sembilan", "sepuluh", "sebelas", "dua belas",
            "tiga belas", "empat belas", "lima belas", "enam belas",
            "tujuh belas", "delapan belas", "sembilan belas", "dua puluh"]
    return kata[n] if 0 <= n < len(kata) else str(n)


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


# ── penyusun blok per bab ────────────────────────────────────────────────────

def _blok_latar_belakang(ctx: dict, args: dict) -> list[tuple]:
    """Bab A.1. Urutan sumber sengaja begini supaya TIDAK menduplikasi bab B.

    Ringkasan obyek di context.md kerap menjadi bahan `gambaran_umum` juga;
    bila keduanya diisi teks yang sama, laporan memuat paragraf kembar. Karena
    itu ringkasan hanya dipakai bila BERBEDA dari gambaran umum, dan bila tidak
    ada, disusun kalimat pengantar dari dasar penugasan.
    """
    teks = (args.get("latar_belakang") or "").strip()
    if not teks:
        ringkas = (ctx.get("ringkasan_obyek") or "").strip()
        gu = (args.get("gambaran_umum") or "").strip()
        if ringkas and ringkas[:120] != gu[:120]:
            teks = ringkas
    if not teks:
        dasar = (args.get("dasar_permintaan") or ctx.get("dasar") or "").strip()
        if dasar:
            teks = (f"Menindaklanjuti {dasar.rstrip('.')}, Inspektorat II "
                    f"melaksanakan {_judul_reviu(args)}.")
    return [P(teks or "[DIISI AUDITOR — latar belakang pelaksanaan reviu]",
              italic=not teks)]


def _blok_dasar(ctx: dict, args: dict) -> list[tuple]:
    dasar = (args.get("dasar_permintaan") or ctx.get("dasar") or "").strip()
    butir: list[str] = []
    if dasar:
        butir.append(dasar if dasar.endswith(".") else dasar + ".")
    st_no = (ctx.get("nomor_st") or "").strip()
    st_tgl = (ctx.get("tanggal_st") or "").strip()
    if st_no:
        # Laporan asli berbunyi "... tentang Melakukan Reviu <obyek>".
        butir.append(
            f"Surat Tugas Inspektur II Nomor {st_no}"
            + (f" tanggal {st_tgl}" if st_tgl else "")
            + f" tentang Melakukan {_judul_reviu(args)}."
        )
    if not butir:
        return [P("[DIISI AUDITOR — dasar pelaksanaan reviu]", italic=True)]
    return [P(f"{i}. {b}", indent=1.3, gantung=0.55)
            for i, b in enumerate(butir, 1)]


def _blok_tujuan(ctx: dict, sasaran: list[dict], args: dict) -> list[tuple]:
    tujuan = (args.get("tujuan") or ctx.get("tujuan") or "").strip()
    if not tujuan:
        tujuan = f"memberikan keyakinan terbatas atas {args.get('judul') or '[DIISI AUDITOR]'}"
    if not tujuan.lower().startswith("tujuan"):
        tujuan_kal = ("Tujuan dari dilaksanakannya reviu adalah untuk "
                      + tujuan[0].lower() + tujuan[1:])
    else:
        tujuan_kal = tujuan
    blok = [P(f"a. {tujuan_kal}", indent=1.3, gantung=0.55),
            P("b. Sasaran dari dilaksanakannya reviu adalah untuk:",
              indent=1.3, gantung=0.55)]
    if sasaran:
        for i, s in enumerate(sasaran, 1):
            d = (s.get("deskripsi") or s.get("sasaran_id") or "").strip()
            if d and not d.endswith((".", ";")):
                d += "."
            blok.append(P(f"{i}. {d}", indent=2.0, gantung=0.55))
    else:
        blok.append(P("1. [DIISI AUDITOR — sasaran reviu]", indent=1.5, italic=True))
    return blok


def _blok_komposisi_tim(ctx: dict) -> list[tuple]:
    tim = ctx.get("tim") or []
    if not tim:
        return [P("[DIISI AUDITOR — susunan tim reviu]", italic=True)]
    baris = [[t.get("no", ""), t.get("nama", ""), t.get("nip", ""), t.get("jabatan", "")]
             for t in tim]
    return [("tabel", ["No", "Nama", "NIP", "Kedudukan dalam Tim"], baris,
             {"lebar": [1.2, 5.6, 4.6, 4.1]})]


def _blok_gambaran_umum(args: dict, komponen: list[dict]) -> list[tuple]:
    gu = (args.get("gambaran_umum") or "").strip()
    blok = [P(gu or "[DIISI AUDITOR — gambaran umum pengadaan]", italic=not gu)]
    if not komponen:
        return blok
    blok.append(P("Berikut adalah rincian komponen dan harga yang akan diadakan:",
                  space_after=4))
    baris, total = [], 0
    for i, k in enumerate(komponen, 1):
        nilai = k.get("nominal")
        try:
            total += int(str(nilai).replace(".", "").replace(",", "")
                         .replace("Rp", "").strip())
        except (TypeError, ValueError):
            pass
        baris.append([str(i), k.get("nama", ""), str(k.get("jumlah", "")),
                      k.get("satuan", ""), _rupiah(nilai)])
    baris.append(["", "TOTAL NOMINAL", "", "", _rupiah(total)])
    blok.append((
        "tabel",
        ["No", "Nama Pengadaan", "Jumlah", "Satuan", "Nominal"],
        baris,
        {"lebar": [1.2, 6.0, 2.0, 2.3, 4.0], "gabung_akhir": 4, "rata_kanan": [4]},
    ))
    return blok


def _blok_hasil_reviu(catatan: list[dict], args: dict, ada_catatan: bool) -> list[tuple]:
    obyek = args.get("judul") or "pengadaan"
    if ada_catatan:
        n = sum(1 for c in catatan if c.get("jenis", "catatan") == "catatan")
        pembuka = (f"Berdasarkan hasil reviu atas {obyek}, tim reviu menyampaikan "
                   f"{n} ({_terbilang_sederhana(n)}) catatan sebagaimana diuraikan "
                   f"berikut ini.")
    else:
        pembuka = f"Berdasarkan hasil reviu atas {obyek}, didapatkan hasil sebagai berikut:"
    blok = [P(pembuka)]
    for i, c in enumerate(catatan, 1):
        judul = (c.get("judul") or "").strip() or f"Catatan {i}"
        blok.append(P(f"{i}. {judul}", bold=True, align="left",
                      indent=1.3, gantung=0.55, space_after=4))
        for potongan in [x.strip() for x in (c.get("narasi") or "").split("\n") if x.strip()]:
            blok.append(P(potongan, indent=0.75))
        # Placeholder tanggapan HANYA untuk catatan (bukan pernyataan positif).
        if c.get("jenis", "catatan") == "catatan":
            blok.append(P(PLACEHOLDER_TANGGAPAN, indent=0.75, italic=True))
    return blok


def _blok_simpulan(args: dict, ada_catatan: bool) -> list[tuple]:
    """Kalimat keyakinan — bentuk 'kecuali' bila masih ada catatan terbuka.

    Tanpa bentuk 'kecuali', laporan bisa menyatakan semuanya sesuai sambil
    mendaftar beberapa catatan di bab sebelumnya.
    """
    obyek = args.get("judul") or "pengadaan"
    if ada_catatan:
        kal = (f"Berdasarkan hasil reviu, tidak terdapat hal-hal yang membuat kami "
               f"yakin bahwa {obyek} tidak sesuai dengan ketentuan pengadaan "
               f"barang/jasa, kecuali hal-hal yang kami ungkapkan pada bagian "
               f"Hasil Reviu di atas.")
    else:
        kal = (f"Berdasarkan hasil reviu, tidak terdapat hal-hal yang membuat kami "
               f"yakin bahwa {obyek} tidak sesuai dengan ketentuan pengadaan "
               f"barang/jasa.")
    return [P(kal)]


def _blok_rekomendasi(butir: list[dict]) -> list[tuple]:
    """Bab E template. Diisi dari `hal_diperhatikan` — hal yang perlu ditindaklanjuti.

    Pada format lama ini berdiri sebagai bab G "Hal-hal yang Harus diperhatikan";
    di template padanannya bab E Rekomendasi, yang kalimat pengantarnya sudah
    tertulis di template ("... merekomendasikan agar:").
    """
    if not butir:
        return [P("[DIISI AUDITOR — rekomendasi/hal yang perlu ditindaklanjuti]",
                  italic=True)]
    blok: list[tuple] = []
    for i, b in enumerate(butir, 1):
        judul = (b.get("judul") or "").strip()
        uraian = (b.get("uraian") or "").strip()
        if judul:
            blok.append(P(f"{i}. {judul}", bold=True, align="left",
                          indent=1.3, gantung=0.55, space_after=4))
            if uraian:
                blok.append(P(uraian, indent=0.75))
        elif uraian:
            blok.append(P(f"{i}. {uraian}", indent=1.3, gantung=0.55))
    return blok


# ── titik masuk ──────────────────────────────────────────────────────────────

def render(folder: Path, args: dict) -> tuple[bool, str, Path | None]:
    """Bangun LHR narasi di atas template resmi. Return (berhasil, pesan, path)."""
    from app.tools.lhr_tools import resolve_lhp_template  # impor malas: cegah lingkar

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

    template = resolve_lhp_template("reviu-pengadaan")
    if template is None or not Path(template).is_file():
        return (False,
                "template LHP reviu-pengadaan tidak ditemukan — periksa "
                "APP_TEMPLATES_PATH/_skeleton-lhp/template-lhp-reviu-pengadaan.docx",
                None)

    ada_catatan = any(c.get("jenis", "catatan") == "catatan" for c in catatan)
    auditi = (args.get("auditi") or "[DIISI AUDITOR]").strip()
    judul = (args.get("judul") or "[DIISI AUDITOR]").strip()

    doc = Document(str(template))

    # 1) Penanda sederhana — identitas surat, cover, dan surat pengantar.
    isi_penanda(doc, {
        "NOMOR_NOTA_DINAS": args.get("nomor_nota_dinas") or "[DIISI AUDITOR]",
        "TANGGAL_NOTA_DINAS": args.get("tanggal_nota_dinas") or "[DIISI AUDITOR]",
        "DASAR_PERMINTAAN": (args.get("dasar_permintaan") or ctx.get("dasar")
                             or "[DIISI AUDITOR]"),
        "NOMOR_ST": ctx.get("nomor_st") or "[DIISI AUDITOR]",
        "TANGGAL_ST": ctx.get("tanggal_st") or "[DIISI AUDITOR]",
        # Template berbunyi "LAPORAN HASIL {{HAL_LHR}}" — judul dari agen
        # lazimnya tanpa kata "Reviu", sehingga tanpa penyesuaian ini cover
        # berbunyi "LAPORAN HASIL Pengadaan ..." yang membalik makna.
        "HAL_LHR": _judul_reviu(args),
        "OBJEK_AUDIT": auditi,
        "PENERIMA_LHP": (args.get("penerima") or ctx.get("penerima_lhp") or auditi),
        "TEMBUSAN_LIST": args.get("tembusan") or "[DIISI AUDITOR]",
        "LINK_SURVEI": args.get("link_survei") or "[DIISI AUDITOR]",
        "A6_JANGKA_WAKTU": ctx.get("periode") or "[DIISI AUDITOR]",
        "NOMOR_LHR": "[DIISI AUDITOR — dari SIMWAS]",
    })

    # 2) Penanda berisi banyak paragraf/tabel.
    tanam = {
        "{{A1_LATAR_BELAKANG}}": _blok_latar_belakang(ctx, args),
        "{{A2_DASAR}}": _blok_dasar(ctx, args),
        "{{A3_TUJUAN}}": _blok_tujuan(ctx, sasaran, args),
        # Isi sub-bab dibiarkan rata tepi kiri — mengikuti kebiasaan template
        # sendiri (lihat bab "Standar Reviu" yang sudah tertulis di sana).
        "{{A4_RUANG_LINGKUP}}": [P(args.get("ruang_lingkup")
                                   or ctx.get("ruang_lingkup") or RUANG_LINGKUP_BAKU)],
        "{{A5_METODOLOGI}}": [P(args.get("metodologi") or METODOLOGI_BAKU)],
        "{{A7_KOMPOSISI_TIM}}": _blok_komposisi_tim(ctx),
        "{{B_GAMBARAN_UMUM}}": _blok_gambaran_umum(
            args, narasi_doc.get("komponen_harga") or []),
        "{{C_HASIL_REVIU}}": _blok_hasil_reviu(catatan, args, ada_catatan),
        "{{D_SIMPULAN}}": _blok_simpulan(args, ada_catatan),
        "{{E_REKOMENDASI}}": _blok_rekomendasi(narasi_doc.get("hal_diperhatikan") or []),
    }
    tak_ketemu = [k for k, blok in tanam.items() if tanam_blok(doc, k, blok) == 0]

    slug = re.sub(r"[^A-Za-z0-9]+", "-", str(ctx.get("nomor_st") or "DRAFT")).strip("-")
    out = folder / "_LHP" / f"LHR-NARASI-{slug}.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        doc.save(str(out))
    except OSError as e:
        return False, f"gagal menyimpan laporan: {e}", None

    n_catatan = sum(1 for c in catatan if c.get("jenis", "catatan") == "catatan")
    pesan = (f"template={Path(template).name}|catatan={n_catatan}"
             f"|positif={len(catatan) - n_catatan}")
    if tak_ketemu:
        # Jangan diam: penanda yang tak ditemukan berarti bagian laporan itu
        # TIDAK terisi — auditor harus tahu, bukan menemukannya sendiri nanti.
        pesan += "|PERINGATAN penanda tak ada di template: " + ", ".join(tak_ketemu)
    return True, pesan, out

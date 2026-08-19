"""Lapisan ekstraksi DETERMINISTIK berbasis LiteParse (run-llama/liteparse).

Motivasi: gantikan/lengkapi pdfplumber + Haiku fallback dengan parser cepat yang:
- 100% local (Apache 2.0 / MIT), tanpa API key
- Mendukung PDF, DOCX, XLSX, PPTX, image (OCR Tesseract bundled)
- Spatial text + bounding box (bisa untuk extraction layout-aware)
- ~1-3 ms/halaman PDF text-based, ~5-20 detik bila perlu OCR

Strategi pakai:
  1. `extract_pages(path)` → list[str] (drop-in replacement `extract_pdf_pages`)
  2. `extract_fields_deterministic(pages, jenis)` → ambil field umum via REGEX
     atas teks LiteParse yang sudah bersih (jauh lebih rapi vs pdfplumber kasar).
  3. Hanya bila field kritis tetap kosong, panggil `llm_extract_fields` (Haiku).

Modul ini TIDAK menyentuh V6 dan TIDAK panggil LLM sama sekali.
"""
from __future__ import annotations

import hashlib
import os
import re
import threading

# LiteParse (parser PDF native) TIDAK thread-safe: memanggil `parse()` dari >1
# thread bersamaan → SEGFAULT yang MEMBUNUH seluruh proses (bukan exception).
# Terjadi saat _run_ingestion men-digest banyak PDF paralel (asyncio.to_thread).
# Serialisasi semua panggilan parse dengan satu lock global — aman & tak mahal.
_PARSE_LOCK = threading.Lock()
from functools import lru_cache
from pathlib import Path
from typing import Iterable

# OCR di-OFF default: dokumen Kominfo digital. Bisa di-toggle via env.
_OCR_DEFAULT = os.environ.get("LITEPARSE_OCR_ENABLED", "0").lower() in ("1", "true", "yes")
_QUIET_DEFAULT = os.environ.get("LITEPARSE_QUIET", "1").lower() in ("1", "true", "yes")


# Ekstensi yang LiteParse handle (PDF native, office via LibreOffice, image via Tesseract).
_LITEPARSE_EXTS = {
    ".pdf",
    ".docx", ".doc", ".odt", ".rtf",
    ".xlsx", ".xls", ".ods", ".csv",
    ".pptx", ".ppt", ".odp",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".webp",
    ".txt", ".md",
}


@lru_cache(maxsize=2)
def _get_parser(ocr_enabled: bool, quiet: bool):
    """Lazy-load LiteParse parser; cached so we tidak ulang setup tiap call."""
    try:
        from liteparse import LiteParse
    except ImportError:  # pragma: no cover — package opsional saat dev
        return None
    return LiteParse(ocr_enabled=ocr_enabled, quiet=quiet)


def is_supported(path: str | Path) -> bool:
    """Cek apakah ekstensi file di-support LiteParse."""
    return Path(path).suffix.lower() in _LITEPARSE_EXTS


def available() -> bool:
    """True bila LiteParse terinstall."""
    return _get_parser(_OCR_DEFAULT, _QUIET_DEFAULT) is not None


# ---------------------------------------------------------------------------
# OCR TERARAH (RapidOCR + PyMuPDF) — untuk PDF hasil pindai & berkas gambar.
# Murni pip (ONNX), TANPA Tesseract/poppler.
#
# KEBIJAKAN (keputusan pengguna, 19 Agu 2026): OCR TIDAK lagi jalan untuk semua
# dokumen. Ia mahal (±1-3 detik/halaman) dan dulu dipakai membabi buta pada
# SETIAP berkas yang teksnya kosong, hanya 8 halaman pertama, lalu hasilnya
# digabung jadi satu blok sehingga nomor halaman HILANG — padahal doktrin
# mewajibkan tiap kutipan membawa nomor halaman. Sekarang:
#
#   • KRITERIA        → hanya halaman yang DITUNJUK auditor di Daftar Kriteria
#   • BUKTI-LAPANGAN  → seluruh berkas, dibatasi OCR_MAX_BUKTI halaman
#   • selebihnya      → TIDAK di-OCR; statusnya dilaporkan jujur ke pengguna
#
# Pemanggil WAJIB meminta OCR eksplisit lewat `ocr_pages()`; `extract_pages()`
# tidak pernah lagi memicu OCR sendiri. Hasil per halaman disimpan (kunci:
# sha256 berkas + nomor halaman) sehingga satu halaman tak pernah di-OCR dua
# kali, bahkan lintas penugasan.
# ---------------------------------------------------------------------------
_RAPIDOCR = None
_RAPIDOCR_TRIED = False
_OCR_IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".tiff", ".webp"}

# Batas halaman OCR untuk bukti lapangan (berita acara/observasi lazimnya pendek).
# Lebih dari ini: sisanya tidak dibaca, TAPI dikatakan terus terang.
OCR_MAX_BUKTI = 10


def _get_rapidocr():
    global _RAPIDOCR, _RAPIDOCR_TRIED
    if _RAPIDOCR_TRIED:
        return _RAPIDOCR
    _RAPIDOCR_TRIED = True
    try:
        from rapidocr_onnxruntime import RapidOCR
        _RAPIDOCR = RapidOCR()
    except Exception:  # noqa: BLE001 — pustaka opsional
        _RAPIDOCR = None
    return _RAPIDOCR


def _ocr_lines_to_text(res) -> str:
    if not res:
        return ""
    try:
        return "\n".join(line[1] for line in res)
    except Exception:  # noqa: BLE001
        return ""


def file_sha256(path: str | Path) -> str:
    """Sidik jari berkas — kunci simpanan hasil OCR."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
    except OSError:
        return ""
    return h.hexdigest()


def _ocr_cache_dir() -> "Path | None":
    """Folder simpanan hasil OCR (di bawah APP_DATA_DIR). None bila tak tersedia."""
    try:
        from app.config import get_settings  # impor malas: hindari lingkar impor

        d = get_settings().data_dir / "_ocr-cache"
        d.mkdir(parents=True, exist_ok=True)
        return d
    except Exception:  # noqa: BLE001 — simpanan itu optimasi, bukan syarat
        return None


def _cache_path(sha: str, halaman: int) -> "Path | None":
    d = _ocr_cache_dir()
    if d is None or not sha:
        return None
    return d / f"{sha}-p{halaman:04d}.txt"


def read_cached_ocr_page(path: str | Path, halaman: int) -> "str | None":
    """Teks OCR sebuah halaman BILA sudah pernah dibaca. Tak pernah meng-OCR baru.

    Dipakai `read_pdf_page` & indeks bukti: keduanya boleh MEMAKAI hasil OCR yang
    sudah ada, tapi tidak boleh memicu pekerjaan OCR baru (mahal, di luar kebijakan).
    """
    cp = _cache_path(file_sha256(Path(path)), int(halaman))
    if cp is None or not cp.is_file():
        return None
    try:
        txt = cp.read_text(encoding="utf-8")
    except OSError:
        return None
    return txt or None


def ocr_pages(
    path: str | Path,
    *,
    pages: "Iterable[int] | None" = None,
    max_pages: int = OCR_MAX_BUKTI,
) -> dict:
    """OCR halaman tertentu (1-based). Return {nomor_halaman: teks}.

    `pages=None` → halaman 1..max_pages. Berkas gambar selalu dianggap 1 halaman.
    Halaman yang sudah pernah di-OCR diambil dari simpanan, tidak diulang.
    Return {} bila pustaka OCR tak tersedia atau berkas tak terbaca.
    """
    p = Path(path)
    ext = p.suffix.lower()
    sha = file_sha256(p)
    hasil: dict = {}

    if ext in _OCR_IMG_EXTS:
        want = [1]
    elif ext == ".pdf":
        want = sorted({int(n) for n in pages}) if pages else []
    else:
        return {}

    def _ambil_simpanan(nomor):
        sisa = []
        for n in nomor:
            cp = _cache_path(sha, n)
            if cp is not None and cp.is_file():
                try:
                    hasil[n] = cp.read_text(encoding="utf-8")
                    continue
                except OSError:
                    pass
            sisa.append(n)
        return sisa

    def _simpan(n, teks):
        cp = _cache_path(sha, n)
        if cp is not None:
            try:
                cp.write_text(teks, encoding="utf-8")
            except OSError:
                pass

    sisa = _ambil_simpanan(want) if want else []
    if want and not sisa:
        return hasil

    ocr = _get_rapidocr()
    if ocr is None:
        return hasil

    try:
        if ext in _OCR_IMG_EXTS:
            res, _ = ocr(str(p))
            teks = _ocr_lines_to_text(res).strip()
            hasil[1] = teks
            _simpan(1, teks)
            return hasil

        import tempfile
        try:
            import fitz  # PyMuPDF
        except Exception:  # noqa: BLE001
            return hasil
        doc = fitz.open(str(p))
        try:
            total = len(doc)
            if want:
                target = sisa
            else:
                target = _ambil_simpanan(list(range(1, min(total, max_pages) + 1)))
            for n in target:
                if n < 1 or n > total:
                    continue
                pix = doc[n - 1].get_pixmap(dpi=200)
                tf = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
                tf.close()
                try:
                    pix.save(tf.name)
                    res, _ = ocr(tf.name)
                    teks = _ocr_lines_to_text(res).strip()
                    hasil[n] = teks
                    _simpan(n, teks)
                finally:
                    try:
                        os.unlink(tf.name)
                    except OSError:
                        pass
        finally:
            doc.close()
    except Exception:  # noqa: BLE001 — OCR gagal = tak ada teks, bukan crash
        return hasil
    return hasil


def pdf_page_count(path: str | Path) -> int:
    """Jumlah halaman PDF (0 bila gagal/bukan PDF). Untuk pesan status jujur."""
    p = Path(path)
    if p.suffix.lower() != ".pdf":
        return 0
    try:
        import fitz

        doc = fitz.open(str(p))
        try:
            return len(doc)
        finally:
            doc.close()
    except Exception:  # noqa: BLE001
        return 0


# ---------------------------------------------------------------------------
# Public API — text extraction
# ---------------------------------------------------------------------------

def extract_pages(
    path: str | Path,
    *,
    ocr: bool | None = None,
    quiet: bool | None = None,
) -> list[str]:
    """Ekstrak teks per-halaman. Return [] bila gagal/tidak support.

    Drop-in replacement untuk `llm_extract.extract_pdf_pages` dengan keunggulan:
    - Lebih cepat (1-3 ms/p PDF tanpa OCR vs 30-80 ms pdfplumber)
    - Layout lebih bersih (kolom angka RAB utuh, bukan tercampur)
    - Multi-format (DOCX/XLSX/PPTX juga di-handle)
    """
    p = Path(path)
    if not p.is_file() or not is_supported(p):
        return []
    # Teks polos (.txt/.md): baca langsung — LiteParse mengembalikan 0 halaman
    # untuk format ini (ketahuan saat uji BUKTI-LAPANGAN: BA .md → digest kosong
    # SENYAP, agen tidak bisa membaca bukti). Tanpa parser juga lebih cepat.
    if p.suffix.lower() in {".txt", ".md"}:
        try:
            return [p.read_text(encoding="utf-8", errors="replace")]
        except OSError:
            return []
    # Office (Word .docx / Excel .xlsx): ekstrak deterministik (bukan lewat
    # LiteParse yang PDF-centric) supaya upload Word/Excel diterima.
    from app.office_extract import extract_office_pages
    office = extract_office_pages(p)
    if office is not None:
        return office
    parser = _get_parser(
        _OCR_DEFAULT if ocr is None else ocr,
        _QUIET_DEFAULT if quiet is None else quiet,
    )
    pages: list[str] = []
    if parser is not None:
        try:
            with _PARSE_LOCK:  # serialisasi — liteparse tidak thread-safe (anti-segfault)
                result = parser.parse(str(p))
        except Exception:  # noqa: BLE001 — rusak/encrypted/gambar → coba OCR
            result = None
        if result is not None:
            for pg in getattr(result, "pages", []) or []:
                pages.append(getattr(pg, "text", "") or "")
            # Bila hanya 1 doc page kosong tapi `result.text` ada (format non-paged).
            if not pages and getattr(result, "text", ""):
                pages = [result.text]
    # OCR TIDAK dipicu di sini (lihat kebijakan di blok OCR di atas). Berkas yang
    # teksnya kosong dikembalikan apa adanya; pemanggil yang berhak meng-OCR
    # (digest KRITERIA & BUKTI-LAPANGAN) memanggil `ocr_pages()` secara eksplisit,
    # dan pemanggil lain melaporkan "tidak terbaca" secara jujur ke pengguna.
    return pages


def extract_full_text(path: str | Path, **kwargs) -> str:
    """Teks satu blob (semua halaman digabung dengan dua newline)."""
    return "\n\n".join(p for p in extract_pages(path, **kwargs) if p)


# ---------------------------------------------------------------------------
# Public API — field extraction REGEX (deterministik, hardcode)
#
# Berlaku pada teks LiteParse yang relatif bersih. Pattern di-tuning untuk
# dokumen perencanaan/pengadaan pemerintah Indonesia (RKA-K/L, KAK, HPS, RFI).
# Tidak panggil LLM. Hanya extract apa yang label-nya eksplisit.
# ---------------------------------------------------------------------------

# Pola label fleksibel: "Label : nilai" / "Label nilai" (tab/space/newline)
def _grab(text: str, labels: Iterable[str]) -> str | None:
    """Cari nilai setelah salah satu label. Case-insensitive, lintas baris.

    Heuristic: label diikuti `:` atau spasi panjang, ambil hingga newline.
    """
    for lbl in labels:
        pat = re.compile(
            rf"(?im)^\s*{re.escape(lbl)}\s*[:\-]?\s*(.+?)$",
        )
        m = pat.search(text)
        if m:
            v = m.group(1).strip(" \t-:")
            # Buang trailing dot/colon/space
            v = re.sub(r"\s+", " ", v).strip()
            if v and v.lower() not in ("none", "null", "-", "n/a"):
                return v
    return None


def _grab_money(text: str, labels: Iterable[str]) -> int | None:
    """Cari nilai uang setelah label. Return int rupiah, atau None.

    PENTING: regex stop di newline supaya tidak menyerap angka kode/baris
    berikutnya (mis. 'Alokasi Dana: Rp 2,450,000,000\\n5241.QDC.001.051').
    """
    for lbl in labels:
        # Hanya match angka dengan separator titik/koma/spasi DI SATU BARIS.
        pat = re.compile(
            rf"(?im){re.escape(lbl)}\s*[:\-]?\s*Rp\.?\s*([0-9][0-9\.\,]*(?:\s[0-9\.\,]+)*)",
        )
        m = pat.search(text)
        if m:
            n = _parse_rupiah(m.group(1))
            if n is not None and n >= 1000:
                return n
    # Fallback: label tanpa "Rp" — masih satu baris saja.
    for lbl in labels:
        pat = re.compile(
            rf"(?im){re.escape(lbl)}\s*[:\-]?\s*([0-9][0-9\.\,]{{4,}})",
        )
        m = pat.search(text)
        if m:
            n = _parse_rupiah(m.group(1))
            # Filter angka kecil (jumlah unit) DAN angka mustahil-besar (>1 triliun =
            # kemungkinan terkonkat dengan kode rincian seperti '5241.QDC.001').
            if n is not None and 1000 <= n < 1_000_000_000_000:
                return n
    return None


_RP_CLEAN_RE = re.compile(r"[^\d]")


def _parse_rupiah(s: str) -> int | None:
    """'2,450,000,000' / '2.450.000.000' / '2 450 000 000' → 2450000000."""
    if not s:
        return None
    cleaned = _RP_CLEAN_RE.sub("", s)
    if not cleaned:
        return None
    try:
        return int(cleaned)
    except ValueError:
        return None


# Pola regulasi: "UU 11/2008", "PP No. 60 Tahun 2008", "Perpres 16/2018",
# "Permenpan RB 5/2019". Output dinormalkan ringkas.
_REGULATION_RE = re.compile(
    r"\b("
    r"UU(?:D)?\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?|"
    r"PP\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?|"
    r"Perpres\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?|"
    r"Permen(?:pan(?:\s*RB)?|keu|kominfo|komdigi)?\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?|"
    r"Perka(?:ban)?\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?|"
    r"Kepres\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?|"
    r"Inpres\s*(?:No\.?\s*|Nomor\s*)?\d+(?:\s*[/Tahun]+\s*\d{4})?"
    r")\b",
    re.IGNORECASE,
)


def _norm_regulation(s: str) -> str:
    """'UU No. 11 Tahun 2008' → 'UU 11/2008'."""
    s = re.sub(r"\bNo\.?\s*|Nomor\s*", "", s, flags=re.IGNORECASE)
    s = re.sub(r"\s*Tahun\s*", "/", s, flags=re.IGNORECASE)
    s = re.sub(r"\s+", " ", s).strip()
    # Standar singkatan
    s = re.sub(r"^uud?\b", "UU", s, flags=re.IGNORECASE)
    s = re.sub(r"^pp\b", "PP", s, flags=re.IGNORECASE)
    s = re.sub(r"^perpres\b", "Perpres", s, flags=re.IGNORECASE)
    s = re.sub(r"^permen", "Permen", s, flags=re.IGNORECASE)
    return s


def extract_dasar_hukum(text: str, max_items: int = 20) -> list[str]:
    """Tarik regulasi yang disebut di dokumen. Dedup, urutkan stabil."""
    seen: dict[str, None] = {}
    for m in _REGULATION_RE.finditer(text):
        norm = _norm_regulation(m.group(1))
        if norm and norm not in seen:
            seen[norm] = None
            if len(seen) >= max_items:
                break
    return list(seen.keys())


# Pola vendor PT/CV/UD/Yayasan. Hindari false-positive ("PT 1" / "PT.").
_VENDOR_RE = re.compile(
    r"\b(?:PT|CV|UD|Yayasan|Koperasi|Firma|Perum|Persero)\.?\s+"
    r"([A-Z][A-Za-z0-9&.,\-' ]{2,80}?)"
    r"(?=[\.\n,;)]|\s{3,}|$)",
    re.MULTILINE,
)


def extract_vendor_names(text: str, max_items: int = 30) -> list[str]:
    """Tarik nama vendor (PT/CV/...). Dedup case-insensitive."""
    seen: dict[str, str] = {}
    for m in _VENDOR_RE.finditer(text):
        full = re.sub(r"\s+", " ", m.group(0)).strip(".,; ")
        key = full.lower()
        if key not in seen and len(full) > 5:
            seen[key] = full
            if len(seen) >= max_items:
                break
    return list(seen.values())


_DATE_RE = re.compile(
    r"\b(\d{1,2})[\s/\-](Jan(?:uari)?|Feb(?:ruari)?|Mar(?:et)?|Apr(?:il)?|Mei|"
    r"Jun(?:i)?|Jul(?:i)?|Agu(?:stus)?|Sep(?:tember)?|Okt(?:ober)?|"
    r"Nov(?:ember)?|Des(?:ember)?)[\s/\-](\d{4})\b",
    re.IGNORECASE,
)
_MONTH_ID = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "mei": 5, "jun": 6,
    "jul": 7, "agu": 8, "sep": 9, "okt": 10, "nov": 11, "des": 12,
}


def extract_dates_iso(text: str, max_items: int = 20) -> list[str]:
    """Tarik tanggal Indonesia → ISO YYYY-MM-DD. Dedup berurut."""
    out: list[str] = []
    seen: set[str] = set()
    for m in _DATE_RE.finditer(text):
        d, mon, y = m.group(1), m.group(2)[:3].lower(), m.group(3)
        mm = _MONTH_ID.get(mon)
        if not mm:
            continue
        try:
            iso = f"{int(y):04d}-{mm:02d}-{int(d):02d}"
        except ValueError:
            continue
        if iso not in seen:
            seen.add(iso)
            out.append(iso)
            if len(out) >= max_items:
                break
    return out


def extract_fields_deterministic(
    pages_text: list[str] | str,
    jenis: str,
) -> dict:
    """Deterministic field extraction berbasis regex atas teks LiteParse.

    `jenis` mempengaruhi field mana yang dicari (TOR/RAB/KAK/HPS/RFI/Kontrak).
    Field yang tidak ditemukan → None. Yang ketemu → string/int/list.

    Tujuan: maksimal coverage SEBELUM jatuh ke Haiku. Setiap field yang
    bisa kita yakini hardcode (label eksplisit) → kita ambil di sini.
    """
    text = pages_text if isinstance(pages_text, str) else "\n\n".join(p for p in pages_text if p)
    if not text:
        return {}

    jenis_lower = (jenis or "").lower()
    out: dict = {}

    # --- Identitas dokumen RKA-K/L (TOR + RAB punya header serupa) ---
    out["kementerian"] = _grab(text, [
        "Kementerian Negara/Lembaga", "Kementerian/Lembaga", "Kementerian",
    ])
    out["program_nama"] = _grab(text, ["Program"])
    out["kegiatan_nama"] = _grab(text, ["Kegiatan"])
    out["ro"] = _grab(text, [
        "Rincian Output", "Rincian Output (RO)", "Klasifikasi Rincian Output",
    ])

    # --- Nilai uang ---
    out["total_biaya"] = _grab_money(text, [
        "Total Biaya", "Total Anggaran", "Alokasi Dana", "Pagu Anggaran",
        "Jumlah Biaya",
    ])
    out["total_pagu"] = _grab_money(text, [
        "Total Pagu", "Pagu RAB", "Jumlah Pagu", "Total Belanja",
    ])
    out["nilai_hps"] = _grab_money(text, [
        "Nilai HPS", "Harga Perkiraan Sendiri", "HPS",
    ])

    # --- Dasar hukum (general regulasi) ---
    regs = extract_dasar_hukum(text)
    if regs:
        out["dasar_hukum"] = regs

    # --- KAK-specific ---
    if "kak" in jenis_lower or "kerangka acuan" in text.lower()[:500]:
        # Untuk KAK: hanya hitung sebagai dasar_hukum_kak bila SEKSI eksplisit "Dasar Hukum" ada
        if re.search(r"(?im)^\s*[A-Z\d.]*\s*Dasar\s+Hukum\b", text):
            out["dasar_hukum_kak"] = regs or []
        else:
            out["dasar_hukum_kak"] = []  # tegas-kan tidak ada seksi
        out["ruang_lingkup"] = _grab(text, [
            "Ruang Lingkup", "Lingkup Pekerjaan", "Lingkup Kegiatan",
        ])
        out["jangka_waktu"] = _grab(text, [
            "Jangka Waktu", "Waktu Pelaksanaan", "Periode Pelaksanaan",
            "Durasi", "Lama Pelaksanaan",
        ])
        out["metode_pemilihan"] = _grab(text, [
            "Metode Pemilihan", "Metode Pengadaan", "Cara Pengadaan",
        ])

    # --- HPS-specific ---
    if "hps" in jenis_lower:
        # Sumber referensi harga: kumpulkan kalimat yang sebut "RFI"/"penawaran" + vendor + nominal
        # Sederhana: kumpulkan vendor + nominal RFI/penawaran di dekat-dekatnya.
        sources: list[dict] = []
        for m in re.finditer(
            r"(PT|CV|UD)\.?\s+([A-Z][\w&., '\-]{2,60})[\s\S]{0,80}?Rp\.?\s*([\d.,]+)",
            text,
        ):
            nama = f"{m.group(1)} {m.group(2)}".strip()
            nilai = _parse_rupiah(m.group(3))
            if nilai and nilai > 1000:
                sources.append({
                    "nama_sumber": nama,
                    "nilai_rupiah": nilai,
                    "tanggal_atau_nomor": None,
                })
                if len(sources) >= 10:
                    break
        if sources:
            out["sumber_referensi_harga"] = sources

    # --- RFI-specific ---
    if "rfi" in jenis_lower:
        vendors = extract_vendor_names(text)
        if vendors:
            out["nama_vendor_rfi"] = vendors

    # --- Kontrak/renewal: tanggal expire ---
    if any(k in text.lower() for k in ("renewal", "perpanjangan", "habis berlaku", "masa berlaku")):
        dates = extract_dates_iso(text)
        if dates:
            # Ambil tanggal pertama yang berada dalam range masuk akal (2025-2030)
            for d in dates:
                if "2024" <= d[:4] <= "2030":
                    out["masa_berlaku_existing"] = d
                    break

    # --- RAB: hitung jumlah komponen (baris angka uang) ---
    if "rab" in jenis_lower:
        # Heuristik: tiap baris yang punya ≥2 angka uang besar dianggap satu komponen.
        n = 0
        for line in text.splitlines():
            money_hits = re.findall(r"[\d.,]{7,}", line)
            big = [x for x in money_hits if _parse_rupiah(x) and _parse_rupiah(x) >= 10_000]
            if len(big) >= 2:
                n += 1
        if n > 0:
            out["jumlah_komponen"] = n

    # Drop key kosong supaya gampang cek coverage
    return {k: v for k, v in out.items() if v not in (None, "", [], {})}


# ---------------------------------------------------------------------------
# Image counter (sinyal bantu dokumen mungkin scan/gambar)
# ---------------------------------------------------------------------------

def analyze_images(path: str | Path) -> dict:
    """Hitung gambar tertanam per halaman.

    LiteParse tidak expose ini langsung; jatuhkan ke pdfplumber bila PDF.
    """
    res = {"total_pages": 0, "total_images": 0, "pages_with_images": 0, "per_page": []}
    p = Path(path)
    if p.suffix.lower() != ".pdf":
        return res
    try:
        import pdfplumber
    except ImportError:
        return res
    try:
        with pdfplumber.open(str(p)) as pdf:
            per_page = [len(pg.images or []) for pg in pdf.pages]
            res["total_pages"] = len(per_page)
            res["per_page"] = per_page
            res["total_images"] = sum(per_page)
            res["pages_with_images"] = sum(1 for n in per_page if n > 0)
    except Exception:  # noqa: BLE001
        pass
    return res

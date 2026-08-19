"""Storage helpers: folder layout per penugasan, hash, baca/tulis file."""
import hashlib
import json
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path

import aiofiles

from app.config import get_settings

settings = get_settings()
log = logging.getLogger(__name__)

# Subfolder standar per penugasan (mengikuti V6)
PENUGASAN_SUBFOLDERS = [
    "00-input",
    "01-peraturan-internal",
    "02-kontrak",
    "03-perencanaan",
    "04-pelaksanaan",
    "05-keuangan",
    "_PKP",
    "_KKP",
    "_LHP",
    "_QA-SAIPI",
    "_INGESTED",
    "_AUDIT-TRAIL",
    "_BUKTI-AI",
    "_FEEDBACK-AGEN",
    "_SUBMIT",
]


def penugasan_folder(kode: str) -> Path:
    """Path absolut folder penugasan, dibuat bila belum ada."""
    folder = settings.data_dir / "penugasan" / kode
    folder.mkdir(parents=True, exist_ok=True)
    for sub in PENUGASAN_SUBFOLDERS:
        (folder / sub).mkdir(exist_ok=True)
    return folder


def gen_kode_penugasan(skill: str) -> str:
    """Generate kode penugasan unik: YYYY-MM-{skill-slug}-{seq}.

    Timestamp menyertakan mikrodetik (3 digit) supaya pembuatan beruntun dalam
    1 detik (mis. auto-promote banyak finding sekaligus) tidak bentrok pada
    constraint unik `kode`.
    """
    now = datetime.utcnow()
    slug = skill.replace("-", "")
    timestamp = now.strftime("%Y%m%d-%H%M%S") + f"{now.microsecond:06d}"
    return f"{now.year}-{now.month:02d}-{slug}-{timestamp}"


async def save_upload(file_bytes: bytes, target_path: Path) -> None:
    """Tulis bytes ke file async."""
    target_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(target_path, "wb") as f:
        await f.write(file_bytes)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _token(n: str, *tokens: str) -> bool:
    """Cocokkan singkatan pendek sebagai KATA UTUH, bukan potongan huruf.

    `"tor" in "catatan-auditor.docx"` bernilai True — audi·TOR· — sehingga
    catatan auditor salah diklasifikasi sebagai TOR. Sama halnya "kak" pada
    "kakanwil", "sp" pada "spip", "st" pada "standar". Pembatas non-huruf
    (spasi, -, _, ., angka, awal/akhir nama) menghilangkan seluruh kelas
    kesalahan itu.
    """
    return any(re.search(rf"(?<![a-z]){t}(?![a-z])", n) for t in tokens)


def classify_doc_by_filename(name: str) -> str:
    """Klasifikasi sederhana jenis dokumen berdasarkan nama file.

    Bisa di-override hasil Ingestion bila konten ternyata beda.
    """
    n = name.lower()
    # CATATAN AUDITOR (skema utama FREE): hasil analisis awal auditor — catatan,
    # draf temuan, konsep KKSA. Dicek PALING AWAL: judul catatan lazimnya memuat
    # nama dokumen yang ditelaah ("catatan-reviu-kontrak", "catatan-HPS"), jadi
    # kalau dicek belakangan ia nyasar ke KONTRAK/HPS/BUKTI-LAPANGAN.
    # Pemisah disamakan jadi spasi lebih dulu — nama file nyata memakai tanda
    # hubung ("draf-temuan-01.docx"), bukan spasi.
    nsp = re.sub(r"[-_.]+", " ", n)
    if (
        "catatan" in nsp or "temuan awal" in nsp or "draf temuan" in nsp
        or "draft temuan" in nsp or "konsep temuan" in nsp or "notulen" in nsp
        or nsp.startswith("cat ") or nsp.startswith("tmn ")
    ):
        return "CATATAN-AUDITOR"
    if _token(n, "tor") or "kerangka acuan" in n:
        return "TOR"
    if _token(n, "rab") or "rincian anggaran" in n:
        return "RAB"
    if _token(n, "kak"):
        return "KAK"
    if _token(n, "hps") or "harga perkiraan" in n:
        return "HPS"
    if _token(n, "rfi"):
        return "RFI"
    if "kontrak" in n or "perjanjian" in n:
        return "KONTRAK"
    # Skill criteria-driven (skill *-umum): auditor unggah kriteria + dokumen objek.
    #
    # Pola diperluas agar SEIRAMA dengan `digest_generic._JENIS_PATTERNS`. Dulu
    # penebak di sini hanya mengenal "kriteria/juknis/juklak", sementara digest
    # mengenal regulasi (permen/perpres/PP/UU/perka) — akibatnya berkas bernama
    # "Permen 5 2024.pdf" ditandai OTHER saat diunggah tapi KRITERIA saat
    # di-digest. Dua sumber kebenaran yang diam-diam melenceng.
    if (
        "kriteria" in n or "juknis" in n or "juklak" in n
        or "pedoman" in n or "kuesioner" in n or "checklist" in n
        or "standar operasional" in n
        or _token(n, "sop")
        or re.search(r"(?<![a-z])(permen|perpres|perpu|perka|perlem|perdirjen|kepmen)(?![a-z])", n)
        or re.search(r"(?<![a-z])(pp|uu|se|perpres)[\s_\-.]*\d", n)
    ):
        return "KRITERIA"
    if "objek" in n or "obyek" in n:
        return "OBJEK"
    # Bukti lapangan AT (opsional; bila ada WAJIB dianalisis agen) — hasil
    # pemeriksaan fisik, observasi lapangan, wawancara/diskusi dengan ahli,
    # berita acara. Cek SEBELUM survey: "observasi"/"ba-" jangan nyasar.
    if (
        "bukti-lapangan" in n or "bukti lapangan" in n
        or "pemeriksaan fisik" in n or "cek fisik" in n or "opname" in n
        or "observasi" in n or "wawancara" in n
        or "diskusi ahli" in n or "keterangan ahli" in n or "tenaga ahli" in n
        or "berita acara" in n or n.startswith("ba-") or n.startswith("ba_")
    ):
        return "BUKTI-LAPANGAN"
    # Survey pendahuluan (audit-*) — memo SP, hasil entry meeting, profil auditi awal.
    if "survey" in n or "survei" in n or _token(n, "sp") or "memo sp" in n:
        return "SURVEY"
    if _token(n, "st") or "surat tugas" in n:
        return "ST"
    if _token(n, "kp") or "kartu penugasan" in n:
        return "KP"
    if _token(n, "pkp") or "program kerja pengawasan" in n:
        return "PKP"
    return "OTHER"


def target_subfolder_for(jenis: str) -> str:
    """Sub-folder default untuk jenis dokumen tertentu."""
    mapping = {
        "ST": "00-input",
        "KP": "00-input",
        "PKP": "00-input",
        "TOR": "03-perencanaan",
        "RAB": "03-perencanaan",
        "KAK": "02-kontrak",
        "HPS": "02-kontrak",
        "RFI": "02-kontrak",
        "KONTRAK": "02-kontrak",
        "KRITERIA": "01-peraturan-internal",  # regulasi/SOP/juknis acuan (criteria-driven)
        "OBJEK": "00-input",                   # dokumen objek pengawasan (criteria-driven)
        "SURVEY": "00-survey",                 # bahan survey pendahuluan audit-* (tahapan 0)
        "BUKTI-LAPANGAN": "04-bukti-lapangan",  # pemeriksaan fisik/observasi/diskusi ahli (AT)
        "CATATAN-AUDITOR": "05-catatan-auditor", # analisis awal auditor — bahan utama skema KKSA
    }
    return mapping.get(jenis, "00-input")


async def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2))


async def read_json(path: Path) -> dict | list:
    async with aiofiles.open(path, "r", encoding="utf-8") as f:
        return json.loads(await f.read())


def _count_temuan(folder: Path) -> int:
    path = folder / "_KKP" / "temuan.json"
    if not path.exists():
        return 0
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return len(data.get("temuan", [])) if isinstance(data, dict) else 0
    except (json.JSONDecodeError, OSError):
        return 0


def _all_sasaran_disetujui(folder: Path) -> bool:
    path = folder / "_PKP" / "sasaran-assignment.json"
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    sasaran = data.get("sasaran", []) if isinstance(data, dict) else []
    return bool(sasaran) and all(s.get("status") == "DISETUJUI_KT" for s in sasaran)


def _all_at_sasaran_submitted(folder: Path) -> bool:
    """True bila semua sasaran ber-assigned_to sudah SELESAI_KKP atau DISETUJUI_KT
    (atau sentinel _KKP/kkp-at-done.flag ada). Transplant tahapan v8 → v10.1:
    dipakai untuk status antara KKP_AT_DONE (AT selesai, menunggu persetujuan KT).
    Status sasaran diset oleh alur v10 (SELESAI_KKP otomatis; DISETUJUI_KT via
    SasaranApprovalPanel), jadi graft ini kompatibel dengan persetujuan per-sasaran.
    """
    if (folder / "_KKP" / "kkp-at-done.flag").exists():
        return True
    sa_path = folder / "_PKP" / "sasaran-assignment.json"
    if not sa_path.exists():
        return False
    try:
        data = json.loads(sa_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    sasaran = data.get("sasaran", []) if isinstance(data, dict) else []
    assigned = [s for s in sasaran if isinstance(s, dict) and s.get("assigned_to")]
    if not assigned:
        return False
    return all(s.get("status") in ("SELESAI_KKP", "DISETUJUI_KT") for s in assigned)


def compute_penugasan_status(folder: Path, dokumen_statuses: list[str], stored_status=None):
    """Turunkan status penugasan dari artefak nyata di disk, bukan dari field DB
    yang tidak pernah dimajukan. Prioritas dari tahap terjauh.

    Catatan: field `Penugasan.status` di DB historically tidak ter-update di
    setiap stage; status display selalu dihitung ulang di sini.
    """
    from app.models import PenugasanStatus  # impor lambat — hindari siklus

    lhp_dir = folder / "_LHP"
    kkp_dir = folder / "_KKP"

    if lhp_dir.exists() and any(
        next(lhp_dir.glob(pat), None) is not None
        for pat in ("LHP-SUBSTANSI*.docx", "LHA-*.docx", "LHR-*.docx", "LHE-*.docx", "LP-*.docx")
    ):
        return PenugasanStatus.LHP_DONE
    if (lhp_dir / "rekomendasi.json").exists():
        return PenugasanStatus.LHP_IN_PROGRESS

    n_temuan = _count_temuan(folder)
    if n_temuan > 0:
        if _all_sasaran_disetujui(folder):
            return PenugasanStatus.KKP_DONE          # gerbang v10: semua sasaran DISETUJUI_KT
        if _all_at_sasaran_submitted(folder):
            return PenugasanStatus.KKP_AT_DONE       # v10.1: AT selesai, menunggu persetujuan KT
        return PenugasanStatus.KKP_IN_PROGRESS

    if any(s == "INGESTING" for s in dokumen_statuses):
        return PenugasanStatus.INGESTING

    # ── Tahap PKP/KP (transplant tahapan v8 → v10.1) ──────────────────────────
    # Berbasis sentinel flag supaya membedakan KT-simpan vs PT-setujui, dan
    # memunculkan tahap KP. Penulis flag ada di routes/penugasan.py.
    pkp_dir = folder / "_PKP"
    if (pkp_dir / "pkp-pt-approved.flag").exists():
        return PenugasanStatus.PKP_DONE              # PT sudah setujui PKP

    # v10.1: PKP_KT_DONE HANYA saat KT eksplisit menyimpan PKP (pkp-kt-saved.flag).
    # Klausa 'or has_sasaran' v8 DIHAPUS — form "Simpan KP" v10 auto-sync sasaran,
    # sehingga "ada sasaran" tak lagi bisa membedakan KP vs PKP; tanpa penghapusan ini
    # status akan loncat ke PKP_KT_DONE dan KP_DONE tak pernah terlihat.
    if (pkp_dir / "pkp-kt-saved.flag").exists():
        return PenugasanStatus.PKP_KT_DONE

    if (pkp_dir / "kp-saved.flag").exists():
        return PenugasanStatus.KP_DONE

    # KOMPATIBILITAS MUNDUR (merge v10.1): penugasan yang dibuat SEBELUM sentinel
    # flag diperkenalkan tidak punya *.flag sama sekali. Tanpa fallback ini,
    # penugasan lama yang sudah ber-PKP (mis. sasaran terisi, temuan belum ada)
    # akan MUNDUR ke DRAFT di UI. Turunkan dari artefak nyata seperti perilaku v10.
    sa_legacy = pkp_dir / "sasaran-assignment.json"
    if sa_legacy.exists():
        try:
            sa = json.loads(sa_legacy.read_text(encoding="utf-8"))
            if isinstance(sa, dict) and sa.get("sasaran"):
                return PenugasanStatus.PKP_DONE
        except (json.JSONDecodeError, OSError):
            pass

    return PenugasanStatus.DRAFT


# Output turunan yang BOLEH dihapus saat re-ingest / re-analisis. Tidak pernah
# menyentuh dokumen sumber, context.md, atau _PKP/sasaran-assignment.json.
def reset_downstream(folder: Path, from_stage: str) -> list[str]:
    """Hapus output turunan supaya re-ingest/re-analisis MENGGANTIKAN (bukan
    menumpuk). `from_stage`:
      - 'ingest'   → _INGESTED + _KKP + _LHP + _QA-SAIPI turunan
      - 'analysis' → _KKP + _LHP + _QA-SAIPI turunan
      - 'lhp'      → _LHP + QC lhp turunan
    Return list path relatif yang dihapus (untuk log/response).
    """
    removed: list[str] = []

    def _rm(path: Path) -> None:
        try:
            if path.is_file():
                path.unlink()
                removed.append(str(path.relative_to(folder)))
        except OSError as e:
            log.warning("reset_downstream: gagal hapus %s: %s", path, e)

    def _glob_rm(subdir: str, patterns: list[str]) -> None:
        d = folder / subdir
        if not d.exists():
            return
        for pat in patterns:
            for p in d.glob(pat):
                _rm(p)

    def _reset_temuan_envelope() -> None:
        path = folder / "_KKP" / "temuan.json"
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        if not isinstance(data, dict):
            return
        envelope = {
            "penugasan": data.get("penugasan", {}),
            "schema_version": data.get("schema_version", "v4.0.0"),
            "temuan": [],
        }
        path.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        removed.append("_KKP/temuan.json (reset → envelope)")

    clear_lhp = from_stage in ("ingest", "analysis", "lhp")
    clear_kkp = from_stage in ("ingest", "analysis")
    clear_ingested = from_stage == "ingest"

    if clear_lhp:
        _glob_rm("_LHP", ["*.docx", "rekomendasi.json"])
        _glob_rm("_QA-SAIPI", ["checklist-lhp.json", "laporan-qa-lhp.md"])
    if clear_kkp:
        _glob_rm("_KKP", [
            "*.docx", "anomalies*.json", "tor-*.json", "rab-*.json", "_pipeline_meta.json",
        ])
        _glob_rm("_QA-SAIPI", ["checklist-kkp.json", "laporan-qa-kkp.md"])
        _reset_temuan_envelope()
    if clear_ingested:
        _glob_rm("_INGESTED", ["*.json"])

    return removed


# Jenis dokumen yang dihitung sebagai "bahan analisis" untuk gate Generate Context
# (criteria-driven). ST/KP/PKP = administratif, bukan bahan analisis.
INPUT_JENIS = {"TOR", "RAB", "KAK", "HPS", "RFI", "KONTRAK", "KRITERIA", "OBJEK", "SURVEY", "OTHER",
               "CATATAN-AUDITOR"}  # catatan auditor = bahan analisis utama di FREE


def context_readiness(
    folder: Path, skill: str | None = None, has_input_docs: bool = False
) -> dict:
    """Prasyarat Generate Context: KT sudah mengisi sasaran + AT sudah unggah
    bahan analisis. "Bahan" tergantung jenis skill:

    - Skill pipeline (reviu-rka-kl/reviu-pengadaan): butuh dokumen ter-digest
      (_INGESTED/*.json) karena context.md disusun dari hasil digest.
    - Skill criteria-driven (audit-kinerja, evaluasi-*, dll): tidak ada digest;
      cukup ada dokumen kriteria/objek yang diunggah (`has_input_docs`, dihitung
      caller dari DB) — agen membaca langsung via read_pdf_page.

    `skill=None` diperlakukan sebagai pipeline (kompatibilitas pemanggil lama).
    """
    from app.skills_registry import LEGACY_SKILLS

    has_sasaran = False
    sa = folder / "_PKP" / "sasaran-assignment.json"
    if sa.exists():
        try:
            d = json.loads(sa.read_text(encoding="utf-8"))
            has_sasaran = bool(isinstance(d, dict) and d.get("sasaran"))
        except (json.JSONDecodeError, OSError):
            pass
    ingested_dir = folder / "_INGESTED"
    has_ingested = ingested_dir.exists() and any(ingested_dir.glob("*.json"))

    skill_norm = str(skill).strip().lower() if skill else None
    is_pipeline = skill_norm is None or skill_norm in LEGACY_SKILLS
    # Pipeline → wajib digest. Criteria-driven → cukup dokumen input (atau digest bila ada).
    has_material = has_ingested if is_pipeline else (has_input_docs or has_ingested)

    reasons: list[str] = []
    if not has_sasaran:
        reasons.append("Ketua Tim belum mengisi sasaran")
    if not has_material:
        if is_pipeline:
            reasons.append("belum ada dokumen ter-digest (AT upload TOR/RAB atau KAK/HPS dulu)")
        else:
            reasons.append("belum ada dokumen kriteria/objek yang diunggah AT")
    return {
        "ready": has_sasaran and has_material,
        "has_sasaran": has_sasaran,
        "has_ingested": has_ingested,
        "has_input_docs": has_input_docs,
        "reason": "; ".join(reasons) if reasons else "Siap generate context",
    }


def delete_penugasan_folder(folder: Path) -> None:
    """Hapus seluruh folder penugasan dari disk (hard delete)."""
    if folder.exists():
        shutil.rmtree(folder, ignore_errors=True)


def delete_file_quiet(path: str | None) -> None:
    """Hapus satu file bila ada; abaikan error."""
    if not path:
        return
    try:
        p = Path(path)
        if p.is_file():
            p.unlink()
    except OSError as e:
        log.warning("delete_file_quiet: gagal hapus %s: %s", path, e)


_INGESTED_PREFIX = {"TOR": "tor", "RAB": "rab"}


def stage_cached_digest(folder: Path, jenis: str, source_json: str | None) -> str | None:
    """Salin hasil digest dari cache ke _INGESTED/ penugasan ini.

    Cache HIT (sha256 sama) cukup men-skip subprocess digest yang mahal, tapi
    file hasilnya tetap harus ada di _INGESTED LOKAL karena tool agen
    (list_ingested / read_ingested_digest) hanya glob folder penugasan ini.
    Penamaan mengikuti konvensi tor-NN.json / rab-NN.json. Return path lokal,
    atau None bila source tidak ada (caller perlakukan sebagai cache miss).
    """
    if not source_json:
        return None
    src = Path(source_json)
    if not src.is_file():
        return None
    ingested_dir = folder / "_INGESTED"
    ingested_dir.mkdir(parents=True, exist_ok=True)
    prefix = _INGESTED_PREFIX.get(jenis, jenis.lower())
    n = len(list(ingested_dir.glob(f"{prefix}-*.json"))) + 1
    dest = ingested_dir / f"{prefix}-{n:02d}.json"
    try:
        shutil.copy2(src, dest)
    except OSError as e:
        log.warning("stage_cached_digest: gagal salin %s → %s: %s", src, dest, e)
        return None
    return str(dest)


def append_audit_trail(folder: Path, event: dict) -> None:
    """Append 1 baris JSON ke _AUDIT-TRAIL/events.jsonl (sync, dipanggil dari tool)."""
    trail_file = folder / "_AUDIT-TRAIL" / "events.jsonl"
    trail_file.parent.mkdir(parents=True, exist_ok=True)
    event["timestamp"] = datetime.utcnow().isoformat() + "Z"
    with open(trail_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")

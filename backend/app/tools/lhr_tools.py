"""Tools untuk Agen Ketua Tim: baca temuan, completeness check, render LHR, QC LHP sync.

Schema rekomendasi.json yang dipakai V6 render_lhp.py:

    {
        "T-001": "Rekomendasi tegas untuk perbaikan...",
        "T-002": "...",
        ...
    }

Note: Function `request_qc_lhp` lama (async-flag) DIGANTI dengan `run_qc_lhp`
sync — sama pola dengan `run_qc_kkp` di kkp_tools.py. Pola lama bermasalah:
agen tidak dapat hasil → improvisasi.
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from claude_agent_sdk import tool
from docx import Document

from app.config import get_settings
from app.tools.v6_bridge import qc_summary_counts, ringkas_gap, run_v6_script, safe_read_json

settings = get_settings()

# Template LHP placeholder-driven, dimiliki app (bukan V6) supaya backend/v6/
# tetap read-only. render_lhp.py V6 menerima override path lewat --template.
_APP_TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"


def _slug(skill: str) -> str:
    return re.sub(r"[^a-z0-9\-]", "-", str(skill).strip().lower())


def resolve_lhp_template(skill: str) -> Path | None:
    """Pilih template LHP per jenis pengawasan.

    Prioritas:
      1. Skeleton per-skill di APP_TEMPLATES_PATH/_skeleton-lhp/template-lhp-[skill].docx
         (placeholder {{...}} V6, satu file per jenis laporan).
      2. Skeleton GENERIK (template-lhp-generic.docx, kata "Reviu"→"Pengawasan")
         untuk skill tanpa skeleton khusus (mis. *-umum, kepatuhan-saipi).
      3. Fallback terakhir: template app reviu-rka-kl (sudah teruji).
    Return path absolut atau None bila tidak ada satupun.
    """
    slug = _slug(skill)
    skel_dir = settings.templates_path / "_skeleton-lhp"
    for candidate in (skel_dir / f"template-lhp-{slug}.docx", skel_dir / "template-lhp-generic.docx"):
        if candidate.is_file():
            return candidate
    fallback = _APP_TEMPLATE_DIR / "template-lhp-reviu-rka-kl.docx"
    return fallback if fallback.is_file() else None


@tool(
    "write_sasaran_assignment",
    "Tulis (overwrite) _PKP/sasaran-assignment.json. PAKAI HANYA di mode 'Setup Penugasan' "
    "saat sasaran-assignment masih kosong/draft. Input `sasaran` adalah list of dict dengan "
    "field: sasaran_id (mis. 'S-PBJ-01'), deskripsi, assigned_to (list[str] nama anggota), "
    "langkah_kerja (list[str]), status (default 'AKTIF'). KT primary path tetap via UI form — "
    "tool ini fallback untuk agent-driven setup.",
    {"penugasan_folder": str, "sasaran": list},
)
async def write_sasaran_assignment(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    path = folder / "_PKP" / "sasaran-assignment.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    raw_sasaran = args.get("sasaran", [])
    if not isinstance(raw_sasaran, list):
        return {
            "content": [{"type": "text", "text": "FAILED|sasaran harus list of dict"}],
            "is_error": True,
        }

    # Normalize + validasi
    sasaran_clean: list[dict] = []
    seen_ids: set[str] = set()
    for s in raw_sasaran:
        if not isinstance(s, dict):
            continue
        sid = str(s.get("sasaran_id", "")).strip()
        if not sid:
            continue
        if sid in seen_ids:
            return {
                "content": [{"type": "text", "text": f"FAILED|sasaran_id duplikat: {sid}"}],
                "is_error": True,
            }
        seen_ids.add(sid)
        assigned = s.get("assigned_to", [])
        if isinstance(assigned, str):
            assigned = [assigned]
        langkah = s.get("langkah_kerja", [])
        if isinstance(langkah, str):
            langkah = [langkah]
        sasaran_clean.append({
            "sasaran_id": sid,
            "deskripsi": str(s.get("deskripsi", "")).strip(),
            "assigned_to": [str(x).strip() for x in assigned if str(x).strip()],
            "langkah_kerja": [str(x).strip() for x in langkah if str(x).strip()],
            "status": str(s.get("status", "AKTIF")).strip() or "AKTIF",
        })

    # Preserve existing envelope kalau file sudah ada, supaya penugasan_id/skill tidak hilang
    existing = safe_read_json(path) if path.exists() else {}
    data = {
        "penugasan_id": existing.get("penugasan_id", folder.name),
        "skill": existing.get("skill", ""),
        "schema_version": "v4.0.0",
        "tanggal_dibuat": datetime.utcnow().isoformat() + "Z",
        "sasaran": sasaran_clean,
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "content": [{
            "type": "text",
            "text": f"OK|total_sasaran={len(sasaran_clean)}|path={path.name}",
        }]
    }


@tool(
    "read_temuan_json",
    "Baca _KKP/temuan.json penugasan SUDAH DIREKONSILIASI dengan keputusan Anggota Tim: "
    "koreksi manual auditor diterapkan, temuan yang ditolak ditandai. Tiap temuan membawa "
    "`_jejak` (asal-usul: AI / AI_DARI_CATATAN / MANUAL, field yang diubah auditor, nilai "
    "asli agen). Susun laporan dari teks yang SUDAH terkoreksi, bukan versi asli agen.",
    {"penugasan_folder": str},
)
async def read_temuan_json(args: dict) -> dict:
    """Temuan + jejak keputusan auditor.

    File `_KKP/temuan.json` menyimpan versi ASLI agen; koreksi Anggota Tim ada
    di DB (`TemuanReview`). Dulu tool ini mengembalikan file mentah, sehingga
    Ketua Tim menyusun laporan dari kalimat yang sudah diperbaiki AT — koreksi
    itu diam-diam hilang, dan temuan yang ditolak AT tetap ikut. Sekarang
    overlay diterapkan di sini (read-only, file tidak disentuh) dan asal-usul
    tiap temuan dibawa serta supaya KT bisa menilai bobotnya.
    """
    folder = Path(args["penugasan_folder"])
    path = folder / "_KKP" / "temuan.json"
    if not path.exists():
        return {
            "content": [{"type": "text", "text": "FAILED|temuan.json tidak ada"}],
            "is_error": True,
        }
    data = safe_read_json(path)

    from app.tools.kkp_tools import load_hitl_annotations

    anotasi = await load_hitl_annotations(folder)
    n_koreksi = 0
    n_ditolak = 0
    hasil: list[dict] = []
    for t in data.get("temuan", []) if isinstance(data, dict) else []:
        if not isinstance(t, dict):
            continue
        tid = t.get("id_temuan")
        a = anotasi.get(tid) or {}
        edits = a.get("edits") or {}
        status = a.get("status") or "PENDING"
        jejak: dict[str, Any] = {
            # Asal-usul temuan: AI (agen menggali sendiri) / AI_DARI_CATATAN
            # (agen merumuskan catatan auditor) / MANUAL (auditor menulis sendiri).
            "origin": t.get("origin", "AI"),
            "status_review": status,
        }
        if edits:
            n_koreksi += 1
            jejak["dikoreksi_auditor"] = True
            jejak["field_diubah"] = a.get("field_diubah") or sorted(edits.keys())
            # Nilai asli agen disertakan agar KT bisa melihat APA yang berubah,
            # bukan sekadar tahu bahwa ada perubahan.
            jejak["versi_asli_agen"] = {k: t.get(k) for k in edits}
            jejak["riwayat_edit"] = a.get("edit_log") or []
        if status == "REJECTED":
            n_ditolak += 1
            jejak["catatan"] = "DITOLAK auditor — JANGAN masukkan ke laporan."
        hasil.append({**t, **edits, "_jejak": jejak})

    if isinstance(data, dict):
        data["temuan"] = hasil
        data["_ringkas_hitl"] = {
            "total": len(hasil),
            "dikoreksi_auditor": n_koreksi,
            "ditolak_auditor": n_ditolak,
            "catatan": (
                "Teks temuan di sini SUDAH memuat koreksi Anggota Tim. "
                "Temuan ber-status REJECTED tidak boleh masuk laporan."
            ),
        }
    return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False)}]}


@tool(
    "check_completeness",
    "Pastikan semua sasaran di sasaran-assignment.json sudah DISETUJUI_KT (sudah di-approve "
    "oleh Ketua Tim). Kalau ada yang masih AKTIF (belum ada temuan) atau SELESAI_KKP "
    "(sudah ada temuan tapi belum approve), STOP — minta KT approve dulu lewat UI Setup.",
    {"penugasan_folder": str},
)
async def check_completeness(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    assignment = safe_read_json(folder / "_PKP" / "sasaran-assignment.json")
    sasaran_list = assignment.get("sasaran", []) if isinstance(assignment, dict) else []

    # Approved statuses yang siap LHR
    APPROVED = {"DISETUJUI_KT"}

    belum = [s for s in sasaran_list if s.get("status") not in APPROVED]
    if belum:
        text = "BELUM_LENGKAP|sasaran_belum=" + json.dumps(
            [
                {
                    "id": s.get("sasaran_id"),
                    "status_current": s.get("status"),
                    "assigned_to": s.get("assigned_to"),
                }
                for s in belum
            ],
            ensure_ascii=False,
        )
        return {"content": [{"type": "text", "text": text}], "is_error": False}
    return {
        "content": [{
            "type": "text",
            "text": f"OK|total_sasaran={len(sasaran_list)}|all_disetujui_kt=true"
        }]
    }


@tool(
    "write_rekomendasi_json",
    "Tulis _LHP/rekomendasi.json — mapping id_temuan ke teks rekomendasi.",
    {"penugasan_folder": str, "rekomendasi": dict},
)
async def write_rekomendasi_json(args: dict) -> dict:
    path = Path(args["penugasan_folder"]) / "_LHP" / "rekomendasi.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(args["rekomendasi"], ensure_ascii=False, indent=2), encoding="utf-8")
    return {"content": [{"type": "text", "text": f"OK|n_rekomendasi={len(args['rekomendasi'])}"}]}


# A1 — penyesuaian jenis (lapisan app, V6 read-only). render_lhp.py menghasilkan
# docx ber-judul "REVIU" generik + nama file LHP-SUBSTANSI; di sini judul/kata &
# nama file disesuaikan per jenis pengawasan: audit→LHA, evaluasi→LHE,
# pemantauan→LP, reviu→LHR.
_JENIS_LABEL = {
    "audit": ("AUDIT", "Audit", "LHA"),
    "kepatuhan": ("AUDIT", "Audit", "LHA"),
    "evaluasi": ("EVALUASI", "Evaluasi", "LHE"),
    "pemantauan": ("PEMANTAUAN", "Pemantauan", "LP"),
    "reviu": ("REVIU", "Reviu", "LHR"),
}


def _jenis_meta(skill: str) -> tuple[str, str, str]:
    s = _slug(skill)
    for key, val in _JENIS_LABEL.items():
        if s.startswith(key):
            return val
    return ("PENGAWASAN", "Pengawasan", "LHP")


def _para_replace(p, subs: list[tuple]) -> None:
    full = "".join(r.text for r in p.runs)
    if not full:
        return
    new = full
    for pat, repl in subs:
        new = pat.sub(repl, new)
    if new != full and p.runs:
        p.runs[0].text = new
        for r in p.runs[1:]:
            r.text = ""


def _family(skill: str) -> str:
    s = _slug(skill)
    for key in ("audit", "kepatuhan", "evaluasi", "pemantauan", "reviu"):
        if s.startswith(key):
            return "audit" if key == "kepatuhan" else key
    return "lain"


def _terbilang(n: int) -> str:
    d = ["nol", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan",
         "sembilan", "sepuluh", "sebelas"]
    return d[n] if 0 <= n < len(d) else str(n)


def _counts(folder: Path) -> tuple[int, int]:
    n = m = 0
    tj = folder / "_KKP" / "temuan.json"
    if tj.exists():
        try:
            d = json.loads(tj.read_text(encoding="utf-8"))
            items = d if isinstance(d, list) else (d.get("temuan") or d.get("items") or [])
            n = len(items)
        except (json.JSONDecodeError, OSError):
            pass
    sj = folder / "_PKP" / "sasaran-assignment.json"
    if sj.exists():
        try:
            d = json.loads(sj.read_text(encoding="utf-8"))
            sas = d.get("sasaran") if isinstance(d, dict) else d
            m = len(sas or [])
        except (json.JSONDecodeError, OSError):
            pass
    return n, m


# A2 — paragraf Metodologi/Intro/Simpulan di-hardcode paradigma REVIU oleh V6
# (read-only). Di lapisan app diganti dengan paragraf sesuai jenis. Paragraf
# diidentifikasi lewat penanda stabil dari teks asli V6.
_SUBSTANCE = {
    "audit": {
        "desk review": "Audit dilaksanakan sesuai Standar Audit Intern Pemerintah Indonesia (SAIPI) melalui penelaahan dokumen, pengujian bukti secara memadai, klarifikasi/wawancara dengan pihak terkait, serta — bila relevan — pemeriksaan dan uji petik atas hasil pekerjaan. Tim juga memanfaatkan analisis pre-digest dan cross-check otomatis untuk mendeteksi anomali antar dokumen.",
        "dikelompokkan ke dalam": "Berdasarkan pengujian atas dokumen dan bukti audit, tim Inspektorat II memperoleh {n} ({nt}) temuan yang dikelompokkan ke dalam {m} ({mt}) aspek sesuai sasaran audit. Temuan dirumuskan dengan paradigma audit (Kondisi-Kriteria-Sebab-Akibat-Rekomendasi) dengan tingkat keyakinan memadai sebagaimana diatur dalam SAIPI.",
        "limited assurance": "Berdasarkan hasil audit yang kami lakukan dengan tingkat keyakinan memadai, terdapat {n} ({nt}) temuan yang perlu ditindaklanjuti auditi sesuai rekomendasi pada laporan ini. Simpulan ini didasarkan pada bukti yang cukup dan memadai; tindak lanjut atas rekomendasi menjadi tanggung jawab pimpinan auditi.",
    },
    "evaluasi": {
        "desk review": "Evaluasi dilaksanakan melalui penelaahan dokumen, analisis data kinerja/capaian, dan klarifikasi kepada unit terkait, dengan membandingkan kondisi yang ada terhadap kriteria evaluasi yang ditetapkan.",
        "dikelompokkan ke dalam": "Berdasarkan penelaahan, tim Inspektorat II memperoleh {n} ({nt}) catatan evaluasi yang dikelompokkan ke dalam {m} ({mt}) aspek sesuai sasaran evaluasi. Catatan dirumuskan dengan paradigma Kondisi-Kriteria-Akibat-Rekomendasi.",
        "limited assurance": "Berdasarkan hasil evaluasi dengan tingkat keyakinan terbatas, terdapat {n} ({nt}) catatan yang perlu ditindaklanjuti untuk meningkatkan kualitas pelaksanaan pada aspek yang dievaluasi.",
    },
    "pemantauan": {
        "desk review": "Pemantauan dilaksanakan melalui penelaahan laporan berkala dan data status pelaksanaan dari auditi/pengawas pekerjaan, dengan membandingkan realisasi terhadap target serta ketentuan kontrak/rencana.",
        "dikelompokkan ke dalam": "Berdasarkan pemantauan, tim Inspektorat II mencatat {n} ({nt}) isu/kondisi yang perlu perhatian, dikelompokkan ke dalam {m} ({mt}) aspek. Kondisi dirumuskan dengan paradigma Kondisi-Kriteria-Sebab-Akibat. Pemantauan bersifat pelaporan status dan tidak memberikan keyakinan atas kebenaran substansi.",
        "limited assurance": "Berdasarkan hasil pemantauan, terdapat {n} ({nt}) kondisi yang perlu perhatian sebagaimana diuraikan. Laporan ini bersifat pelaporan status — tidak memberikan keyakinan dan tidak menyimpulkan pelanggaran; tindak lanjut menjadi kewenangan pihak pengelola kegiatan.",
    },
}


def _set_para(p, text: str) -> None:
    if p.runs:
        p.runs[0].text = text
        for r in p.runs[1:]:
            r.text = ""
    else:
        p.text = text


def _apply_jenis(docx_path: Path, family: str, up: str, title: str, n: int, m: int) -> None:
    """A2 substance (paragraf per jenis) + A1 wording (kata Reviu→jenis). Untuk non-reviu."""
    subst = _SUBSTANCE.get(family, {})
    fmt = {"n": n, "nt": _terbilang(n), "m": m, "mt": _terbilang(m)}
    subs = [
        (re.compile(r"\bREVIU\b"), up),
        (re.compile(r"\bReviu\b"), title),
        (re.compile(r"\breviu\b"), title.lower()),
    ]
    doc = Document(str(docx_path))

    def handle(p):
        for marker, tpl in subst.items():
            if marker in p.text:
                _set_para(p, tpl.format(**fmt))
                return
        _para_replace(p, subs)

    for p in doc.paragraphs:
        handle(p)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    handle(p)
    for sec in doc.sections:
        for area in (sec.header, sec.footer):
            for p in area.paragraphs:
                _para_replace(p, subs)
    doc.save(str(docx_path))


def _finalize_jenis(folder: Path, skill: str) -> str | None:
    """A1 nama-file + A2 substansi/kata per jenis. Return nama file final."""
    up, title, prefix = _jenis_meta(skill)
    family = _family(skill)
    outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"), key=lambda p: p.stat().st_mtime)
    if not outs:
        return None
    produced = outs[-1]
    adaptasi_warn: str | None = None
    if family != "reviu":
        try:
            n, m = _counts(folder)
            _apply_jenis(produced, family, up, title, n, m)
        except Exception as exc:  # noqa: BLE001
            # JANGAN telan senyap: tanpa adaptasi, LHA/LHE bisa terbit masih
            # berbunyi "REVIU"/keyakinan terbatas utk penugasan audit (audit #E6).
            adaptasi_warn = f"adaptasi jenis GAGAL ({type(exc).__name__}: {exc}) — periksa paradigma/metodologi di dokumen"
    final = produced.with_name(produced.name.replace("LHP-SUBSTANSI", prefix, 1))
    if final != produced:
        produced.replace(final)
    if adaptasi_warn:
        return f"{final.name}|WARNING:{adaptasi_warn}"
    return final.name


# ── Data laporan yang V6 cari di tempat yang salah ───────────────────────────
# Dua isi bab LHR tinggal di berkas TERPISAH, sedangkan `render_lhp.py` (mesin
# baca-saja) mencarinya di dalam `_KKP/temuan.json`:
#
#   bab D "Hasil Reviu"           → V6 baca `temuan.json["aspek_reviu"]`,
#                                   data aslinya di `_KKP/penilaian-aspek.json`
#   bab E "Catatan & Rekomendasi" → V6 baca `temuan[i]["rekomendasi"]`,
#                                   data aslinya di `_LHP/rekomendasi.json`
#
# Akibatnya bab D terbit sebagai penanda "[DIISI — ...]" dan bab E hanya memuat
# JUDUL temuan tanpa satu pun rekomendasi — padahal keduanya sudah disusun
# lengkap oleh Anggota Tim. (Ditemukan 26 Agu 2026 pada LHR penugasan 2:
# 9 penilaian aspek dan 4 rekomendasi hilang dari laporan tanpa pesan galat.)
#
# Alih-alih menambal V6, keduanya dititipkan ke `temuan.json` sesaat sebelum
# render lalu dipulihkan — pola yang sama dengan overlay HITL di atasnya.

# Kosakata Anggota Tim → kosakata template LHR. `TIDAK_CUKUP_DATA` sengaja TIDAK
# dipetakan ke "TERPENUHI DENGAN CATATAN": aspek yang datanya belum cukup bukan
# aspek yang terpenuhi, dan laporan resmi tidak boleh memberi keyakinan atas
# sesuatu yang belum diuji.
_STATUS_ASPEK = {
    "SESUAI": "TERPENUHI",
    "TIDAK_SESUAI": "TIDAK TERPENUHI",
    "TIDAK_CUKUP_DATA": "TIDAK DAPAT DISIMPULKAN",
}


def _sambung_data_terpisah(folder: Path, sambung_aspek: bool = True) -> Path | None:
    """Titipkan penilaian aspek + rekomendasi ke `temuan.json` sebelum V6 baca.

    Return path backup; pemanggil WAJIB memanggil `_restore_temuan_from_backup`
    di `finally`. Return None bila tak ada yang perlu disambung.
    """
    temuan_path = folder / "_KKP" / "temuan.json"
    if not temuan_path.is_file():
        return None
    try:
        data = json.loads(temuan_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None  # best-effort — jangan gagalkan render gara-gara penyambungan

    berubah = False

    # bab D — penilaian per aspek (termasuk yang SESUAI, supaya CAKUPAN reviu
    # terlihat di laporan, bukan cuma daftar masalah).
    p_aspek = folder / "_KKP" / "penilaian-aspek.json"
    if sambung_aspek and not data.get("aspek_reviu") and p_aspek.is_file():
        try:
            rows = json.loads(p_aspek.read_text(encoding="utf-8")).get("aspek") or []
        except (OSError, ValueError):
            rows = []
        aspek = []
        for r in rows:
            nama = str(r.get("aspek") or "").strip()
            if not nama:
                continue
            asal = str(r.get("kesimpulan") or "").strip().upper()
            aspek.append({
                "nama": nama,
                "status": _STATUS_ASPEK.get(asal, asal or "TIDAK DAPAT DISIMPULKAN"),
                "keterangan": str(r.get("dasar") or "").strip(),
            })
        if aspek:
            data["aspek_reviu"] = aspek
            berubah = True

    # bab E — rekomendasi per temuan (id_temuan → teks).
    p_rek = folder / "_LHP" / "rekomendasi.json"
    if p_rek.is_file():
        try:
            rek = json.loads(p_rek.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            rek = {}
        if isinstance(rek, dict):
            for t in data.get("temuan") or []:
                if str(t.get("rekomendasi") or "").strip():
                    continue  # sudah terisi — jangan ditimpa
                nilai = rek.get(t.get("id_temuan"))
                if isinstance(nilai, dict):
                    nilai = nilai.get("rekomendasi")
                nilai = str(nilai or "").strip()
                if nilai:
                    t["rekomendasi"] = nilai
                    berubah = True

    if not berubah:
        return None

    backup = folder / "_KKP" / "temuan-sambung-backup.json"
    backup.write_bytes(temuan_path.read_bytes())
    temuan_path.write_text(json.dumps(data, ensure_ascii=False, indent=2),
                          encoding="utf-8")
    return backup


# Kalimat metodologi baku untuk penugasan REVIU — sama dengan yang dipakai
# perender narasi reviu-pengadaan, supaya kedua skill berbunyi sama.
# Enam kalimat bawaan V6 untuk sub-bab C1–C6 reviu-rka-kl. Kalimat ini dicetak
# saat tidak ada temuan yang ter-klasifikasi pada aspeknya — padahal TIDAK ADA
# satu pun prompt/skill yang menyuruh agen mengisi field `area` yang jadi dasar
# klasifikasi itu. Akibatnya laporan menyatakan "telah sesuai" walaupun ada
# temuan: bukan bab kosong, melainkan KEYAKINAN PALSU. (Ditemukan 26 Agu 2026.)
_KLAIM_RKAKL = (
    "Kelayakan SBM/SBK telah sesuai dengan ketentuan.",
    "Kaidah penganggaran telah dipatuhi.",
    "Penandaan tematik telah dilakukan dengan tepat.",
    "Dokumen pendukung telah lengkap.",
    "Kelayakan rincian baru telah memadai.",
    "Pengalokasian tematik telah sesuai arahan.",
)
_TANPA_KLASIFIKASI = (
    "Terdapat temuan hasil reviu yang belum diklasifikasikan menurut aspek ini pada "
    "kertas kerja, sehingga status aspek ini tidak dapat disimpulkan dari laporan. "
    "Uraian seluruh temuan disajikan pada bab Rekomendasi."
)


# ── Bab Hasil Audit (audit-umum) ─────────────────────────────────────────────
# V6 mencetak bab ini dalam bentuk kertas kerja: dikelompokkan per sasaran
# ("F.1. Memastikan ..."), lalu tiap temuan diurai dengan label telanjang
# "Kondisi:/Kriteria:/Sebab:/Akibat:". Auditor menghendaki bentuk yang dipakai
# LHA Inspektorat II sesungguhnya (27 Agu 2026): langsung ke temuan, dinomori
# lurus, dan unsurnya dirangkai kalimat penyambung — enak dibaca pimpinan dan
# objek audit, bukan format kertas kerja yang ditempel.

def _periksa_catatan_vs_temuan(folder: Path) -> str | None:
    """Pastikan catatan laporan = temuan kertas kerja. Return pesan galat / None.

    PEMBAGIAN PERAN (arahan auditor 27 Agu 2026): temuan dibuat ANGGOTA TIM di
    kertas kerja; KETUA TIM merangkainya jadi laporan dan menyusun rekomendasi.
    Ketua Tim boleh mengubah KATA-KATANYA — itu memang tugasnya — tetapi TIDAK
    boleh mengubah DAFTAR temuannya.

    Sebelum pemeriksaan ini, bab Hasil pada jalur narasi diisi persis apa yang
    ditulis agen: temuan karangan bisa terbit di laporan resmi, dan temuan asli
    bisa hilang, tanpa satu pun peringatan. Terbukti lewat percobaan pada
    penugasan nyata 27 Agu 2026.

    Catatan ber-`jenis: positif` DIKECUALIKAN: itu pernyataan kepatuhan atas
    sasaran yang tidak bertemuan, bukan temuan.
    """
    kkp = safe_read_json(folder / "_KKP" / "temuan.json") or {}
    temuan = kkp.get("temuan") or []
    if not temuan:
        return None  # tak ada kertas kerja untuk dibandingkan
    sah = {str(t.get("id_temuan") or "").strip() for t in temuan}
    sah.discard("")

    catatan = (safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}).get("catatan") or []
    dipakai: set[str] = set()
    tanpa_sumber: list[str] = []
    asing: list[str] = []
    for c in catatan:
        if str(c.get("jenis") or "catatan").lower().startswith("pos"):
            continue
        idt = str(c.get("id_temuan") or "").strip()
        judul = str(c.get("judul") or "")[:60]
        if not idt:
            tanpa_sumber.append(judul)
        elif idt not in sah:
            asing.append(f"{idt} ({judul})")
        else:
            dipakai.add(idt)

    hilang = sorted(sah - dipakai)
    galat: list[str] = []
    if tanpa_sumber:
        galat.append("catatan tanpa `id_temuan`: " + "; ".join(tanpa_sumber))
    if asing:
        galat.append("id_temuan tidak ada di kertas kerja: " + "; ".join(asing))
    if hilang:
        galat.append("temuan kertas kerja belum dinarasikan: " + ", ".join(hilang))
    if not galat:
        return None
    return (
        "Catatan laporan tidak cocok dengan temuan kertas kerja. " + " | ".join(galat)
        + ". Temuan dibuat Anggota Tim; tugasmu MERANGKAI temuan itu jadi laporan dan "
        "menyusun rekomendasi — bukan menambah temuan baru atau menghilangkan yang ada. "
        "Kamu bebas menyusun ulang kalimatnya, tapi daftar temuannya harus sama persis "
        "dengan `_KKP/temuan.json` (cek lewat `read_temuan_json`)."
    )


def _daftar(nilai) -> list[str]:
    """Terima list ATAU teks berbaris; kembalikan daftar butir bersih."""
    if isinstance(nilai, list):
        butir = [str(x).strip() for x in nilai]
    else:
        butir = [b.strip(" -•\t") for b in str(nilai or "").split("\n")]
    return [b for b in butir if b]


def _sisip_tabel(doc, jangkar, judul: str, kolom: list, baris: list) -> None:
    """Sisipkan tabel bergaris sebelum `jangkar`, dengan judul di atasnya."""
    from copy import deepcopy

    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
    from docx.text.paragraph import Paragraph

    if judul:
        baru = deepcopy(jangkar._p)
        jangkar._p.addprevious(baru)
        par = Paragraph(baru, jangkar._parent)
        _set_para(par, judul)
        for r in par.runs:
            r.bold = True
            r.italic = False
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER

    tab = doc.add_table(rows=len(baris) + 1, cols=len(kolom))
    tab.style = "Table Grid"
    for j, h in enumerate(kolom):
        sel = tab.rows[0].cells[j]
        sel.text = ""
        run = sel.paragraphs[0].add_run(str(h))
        run.bold = True
        run.font.size = Pt(10)
        sel.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for i, brs in enumerate(baris, 1):
        for j, nilai in enumerate(brs[:len(kolom)]):
            sel = tab.rows[i].cells[j]
            sel.text = ""
            run = sel.paragraphs[0].add_run(str(nilai))
            run.font.size = Pt(10)
    jangkar._p.addprevious(tab._element)
    # paragraf kosong pemisah supaya tabel tidak menempel ke teks berikutnya
    kosong = deepcopy(jangkar._p)
    jangkar._p.addprevious(kosong)
    _set_para(Paragraph(kosong, jangkar._parent), "")


def _kecilkan_awal(teks: str) -> str:
    """Sambung akibat ke "Hal tersebut mengakibatkan ..." tanpa huruf besar nyempil."""
    teks = teks.strip()
    if not teks:
        return ""
    # Jangan kecilkan singkatan/nama diri yang memang berhuruf besar semua.
    if len(teks) > 1 and teks[1].isupper():
        return teks
    return teks[0].lower() + teks[1:]


def _blok_hasil_audit(folder: Path) -> list[tuple] | None:
    """Susun isi bab Hasil Audit dari narasi Ketua Tim.

    Bahannya tetap kertas kerja Anggota Tim, tetapi yang masuk laporan adalah
    tulisan Ketua Tim — bukan salinan mentah satu kolom `temuan.json` jadi satu
    paragraf. Kalimat penyambung ("Kondisi tersebut tidak sesuai dengan:" dst)
    ditambahkan di sini supaya seragam di seluruh laporan.

    Return daftar item: ("p", teks, tebal) atau ("tabel", judul, kolom, baris).
    """
    catatan = (safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}).get("catatan") or []
    if not catatan:
        return None
    blok: list[tuple] = []
    for i, c in enumerate(catatan, 1):
        blok.append(("p", f"{i}. {str(c.get('judul') or f'Temuan {i}').strip()}", True))
        blok.append(("p", "Kondisi", True))
        for b in _daftar(c.get("narasi")):
            blok.append(("p", b, False))
        for t in (c.get("tabel") or []):
            blok.append(("tabel", str(t.get("judul") or "").strip(),
                         list(t.get("kolom") or []), list(t.get("baris") or [])))
        kriteria = _daftar(c.get("kriteria"))
        if kriteria:
            blok.append(("p", "Kondisi tersebut tidak sesuai dengan:", False))
            for j, b in enumerate(kriteria, 1):
                blok.append(("p", b if len(kriteria) == 1 else f"{j}. {b}", False))
        sebab = _daftar(c.get("sebab"))
        if sebab:
            blok.append(("p", "Hal tersebut disebabkan:", False))
            for j, b in enumerate(sebab, 1):
                blok.append(("p", b if len(sebab) == 1 else f"{j}. {b}", False))
        akibat = str(c.get("akibat") or "").strip()
        if akibat:
            blok.append(("p", f"Hal tersebut mengakibatkan {_kecilkan_awal(akibat)}", False))
    return blok


def _tulis_ulang_hasil_audit(docx_path: Path, folder: Path) -> bool:
    """Ganti isi bab Hasil Audit dengan bentuk mengalir. Return berhasil?"""
    from copy import deepcopy

    from docx.text.paragraph import Paragraph

    blok = _blok_hasil_audit(folder)
    if not blok:
        return False
    doc = Document(str(docx_path))
    par = doc.paragraphs
    awal = next((k for k, x in enumerate(par)
                 if x.text.strip().startswith("Berdasarkan audit yang telah dilakukan")), None)
    akhir = next((k for k in range(awal + 1, len(par))
                  if par[k].text.strip() == "BAB IV"), None) if awal is not None else None
    if awal is None or akhir is None:
        return False

    donor = par[awal]
    for item in blok:
        if item[0] == "tabel":
            _sisip_tabel(doc, par[akhir], item[1], item[2], item[3])
            continue
        baru = deepcopy(donor._p)
        par[akhir]._p.addprevious(baru)
        salinan = Paragraph(baru, donor._parent)
        _set_para(salinan, item[1])
        for r in salinan.runs:
            r.bold = item[2]
            r.italic = False
    for k in range(awal + 1, akhir):
        par[k]._p.getparent().remove(par[k]._p)
    doc.save(str(docx_path))
    return True


# ── LHE evaluasi-umum ────────────────────────────────────────────────────────
# Keluaran evaluasi berlapis dua (SKILL.md "Kerangka Penilaian"): penilaian
# BERSKOR per dimensi -> skor total + predikat, DAN temuan K/K/S/A untuk hal
# yang membutuhkan rekomendasi sistem. Bab E memuat lapis pertama, bab F lapis
# kedua — keduanya berbeda peran, bukan kembar.
#
# Skor dibaca LANGSUNG dari `_KKP/penilaian-lke-<skill>.json`. Penerjemah skor
# di V6 sengaja TIDAK dipakai: ia hanya mengenali tujuh nama komponen baku
# SAKIP/SPIP dan MEMBUANG dimensi bernama lain tanpa pesan — sedangkan dimensi
# evaluasi-umum diturunkan bebas dari kriteria yang diunggah auditor.

def _baca_lke(folder: Path, skill: str) -> dict:
    """Rekap skor per dimensi apa adanya (tanpa pemetaan nama baku)."""
    d = safe_read_json(folder / "_KKP" / f"penilaian-lke-{_slug(skill)}.json")
    return d if isinstance(d, dict) else {}


def _komponen_lke(lke: dict) -> list[dict]:
    komp = lke.get("komponen")
    return [k for k in komp if isinstance(k, dict) and str(k.get("nama") or "").strip()] \
        if isinstance(komp, list) else []


def _nilai_komponen(k: dict):
    """Nilai APIP diutamakan — laporan ini produk penjaminan, bukan penilaian mandiri."""
    for kunci in ("nilai_apip", "nilai", "nilai_pm"):
        if k.get(kunci) is not None:
            return k[kunci]
    return None


def _teks_angka(nilai) -> str:
    if nilai is None or nilai == "":
        return ""
    if isinstance(nilai, (int, float)):
        teks = f"{nilai:.2f}".rstrip("0").rstrip(".")
        return teks.replace(".", ",")
    return str(nilai)


def _total_bobot(komp: list[dict]):
    jml = 0.0
    ada = False
    for k in komp:
        try:
            jml += float(k.get("bobot"))
            ada = True
        except (TypeError, ValueError):
            continue
    return jml if ada else None


def _total_lke(lke: dict) -> dict:
    for kunci in ("total_apip", "total", "total_pm"):
        nilai = lke.get(kunci)
        if isinstance(nilai, dict):
            return nilai
        if nilai is not None:
            return {"nilai": nilai, "predikat": lke.get("predikat_akhir") or ""}
    return {}


def _blok_tujuan_sasaran(folder: Path, ctx: dict) -> list[tuple]:
    """B — Tujuan dan Sasaran, dua butir terpisah seperti LHE Inspektorat II."""
    sa = safe_read_json(folder / "_PKP" / "sasaran-assignment.json") or {}
    tujuan = str(ctx.get("tujuan") or "").strip()
    blok: list[tuple] = []
    if tujuan:
        blok.append(("p", f"a. Tujuan dari dilaksanakannya evaluasi adalah "
                          f"{_kecilkan_awal(tujuan)}", False))
    sasaran = [str(x.get("deskripsi") or "").strip()
               for x in (sa.get("sasaran") or []) if str(x.get("deskripsi") or "").strip()]
    if len(sasaran) == 1:
        blok.append(("p", f"b. Sasaran dari dilaksanakannya evaluasi adalah "
                          f"{_kecilkan_awal(sasaran[0])}", False))
    elif sasaran:
        blok.append(("p", "b. Sasaran dari dilaksanakannya evaluasi adalah:", False))
        for i, x in enumerate(sasaran, 1):
            blok.append(("p", f"{i}) {x}", False))
    return blok


def _blok_ruang_lingkup(ruang_lingkup: str) -> list[tuple] | None:
    if not ruang_lingkup.strip():
        return None
    return [("p", f"Ruang lingkup evaluasi adalah {_kecilkan_awal(ruang_lingkup)}", False)]


def _blok_metodologi(ctx: dict) -> list[tuple]:
    teks = str(ctx.get("metodologi") or "").strip() or (
        "Evaluasi dilaksanakan melalui penelaahan dokumen dan data pada sistem "
        "informasi terkait, dilengkapi dengan konfirmasi dan diskusi terbatas dengan "
        "pihak-pihak yang berkepentingan atas objek yang dievaluasi.")
    return [("p", teks, False)]


def _blok_hasil_evaluasi(folder: Path, lke: dict) -> list[tuple] | None:
    """E — tabel (bila ada) + narasi + temuan bernomor, ditulis MENGALIR.

    Mengikuti LHE Inspektorat II: temuan berada DI DALAM bab Hasil Evaluasi,
    tanpa label "Kondisi:/Kriteria:/Sebab:/Akibat:" — unsur itu dirangkai Ketua
    Tim jadi kalimat. Skor per dimensi HANYA dicetak bila instrumen LKE memang
    ada; tanpa LKE, evaluasi tidak menghasilkan skor (arahan auditor 27 Agu 2026).
    """
    narasi = safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}
    catatan = narasi.get("catatan") or []
    blok: list[tuple] = []

    komp = _komponen_lke(lke)
    if komp:
        blok.append(("p", "Rekapitulasi hasil penilaian per dimensi disajikan pada "
                          "tabel berikut:", False))
        blok.extend(_tabel_skor(komp, lke))
        total = _total_lke(lke)
        if total.get("nilai") is not None or total.get("predikat"):
            kal = "Secara keseluruhan objek evaluasi memperoleh nilai "
            kal += _teks_angka(total.get("nilai")) if total.get("nilai") is not None else "-"
            if total.get("predikat"):
                kal += f" dengan predikat {total['predikat']}"
            blok.append(("p", kal.rstrip(".") + ".", False))

    pengantar = str(narasi.get("pengantar_hasil") or "").strip()
    if pengantar:
        for b in _daftar(pengantar):
            blok.append(("p", b, False))

    if catatan:
        # "Atas kondisi tersebut" hanya masuk akal bila ADA kondisi yang diuraikan
        # lebih dulu; tanpa pengantar, kalimatnya menggantung tanpa rujukan.
        pembuka = ("Atas kondisi tersebut, Inspektorat II mencatat temuan sebagai berikut:"
                   if blok else
                   "Berdasarkan hasil evaluasi, Inspektorat II mencatat temuan sebagai berikut:")
        blok.append(("p", pembuka, False))
        for i, c in enumerate(catatan, 1):
            blok.append(("p", f"{i}. {str(c.get('judul') or f'Temuan {i}').strip()}", True))
            for b in _daftar(c.get("narasi")):
                blok.append(("p", b, False))
            for t in (c.get("tabel") or []):
                blok.append(("tabel", str(t.get("judul") or "").strip(),
                             list(t.get("kolom") or []), list(t.get("baris") or [])))
    return blok or None


def _tabel_skor(komp: list[dict], lke: dict) -> list[tuple]:
    baris = []
    for k in komp:
        nilai, bobot = _nilai_komponen(k), k.get("bobot")
        persen = ""
        try:
            if bobot not in (None, "", 0) and nilai is not None:
                persen = f"{float(nilai) / float(bobot) * 100:.2f}".replace(".", ",")
        except (TypeError, ValueError, ZeroDivisionError):
            persen = ""
        baris.append([str(k.get("nama") or ""), _teks_angka(bobot), _teks_angka(nilai),
                      persen, str(k.get("predikat") or "")])
    jml = _jumlah_nilai(komp)
    if jml is not None:
        baris.append(["Jumlah", _teks_angka(_total_bobot(komp)), _teks_angka(jml), "",
                      str(_total_lke(lke).get("predikat") or "")])
    return [("tabel", "Tabel 1. Rekapitulasi Hasil Penilaian per Dimensi",
             ["Dimensi", "Bobot", "Skor", "% Capaian", "Predikat"], baris)]


def _jumlah_nilai(komp: list[dict]):
    """Total DIHITUNG dari komponen — angka total yang dikirim agen tidak dipercaya.

    Tanpa ini laporan bisa mencetak baris "Jumlah" yang tidak nyambung dengan
    baris-baris di atasnya (terbukti 27 Agu 2026: komponen berjumlah 40,
    tercetak 95).
    """
    jml, ada = 0.0, False
    for k in komp:
        try:
            jml += float(_nilai_komponen(k))
            ada = True
        except (TypeError, ValueError):
            continue
    return jml if ada else None


def _butir_rekomendasi(folder: Path) -> list[tuple] | None:
    """Rekomendasi bernomor dari rekomendasi.json, urut mengikuti temuan."""
    rek = safe_read_json(folder / "_LHP" / "rekomendasi.json") or {}
    kkp = safe_read_json(folder / "_KKP" / "temuan.json") or {}
    butir = []
    for t in (kkp.get("temuan") or []):
        nilai = rek.get(str(t.get("id_temuan") or ""))
        if isinstance(nilai, dict):
            nilai = nilai.get("rekomendasi")
        nilai = str(nilai or "").strip()
        if nilai:
            butir.append(nilai)
    return [("p", f"{i}. {b}", False) for i, b in enumerate(butir, 1)] or None


def _blok_rekomendasi_evaluasi(folder: Path) -> list[tuple] | None:
    butir = _butir_rekomendasi(folder)
    if not butir:
        return None
    return [("p", "Berdasarkan kondisi-kondisi tersebut, Inspektorat II "
                  "merekomendasikan agar:", False)] + butir


# Jarak sebelum judul bab. Dipakai spasi-sebelum-paragraf, BUKAN paragraf kosong:
# paragraf kosong bisa terbawa/terhapus saat isi bab disusun ulang, sedangkan
# setelan spasi menempel pada judulnya yang tidak pernah dibuang.
JARAK_ANTAR_BAB_PT = 12


def _seragamkan(doc, dari: str, sampai: str) -> None:
    """Samakan huruf & perataan antar-bab (Arial 12, justify) + jarak antar bab."""
    import re

    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

    par = doc.paragraphs
    i = next((k for k, x in enumerate(par) if x.text.strip().startswith(dari)), None)
    j = next((k for k, x in enumerate(par) if x.text.strip().startswith(sampai)), None)
    if i is None or j is None:
        return
    for urut, x in enumerate(par[i:j + 1]):
        teks = x.text.strip()
        if not teks:
            continue
        if x.paragraph_format.alignment is None:
            x.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        # Judul bab (A. ... G.) diberi jarak dari isi bab sebelumnya — kecuali
        # bab pertama, yang sudah menempel pada surat pengantar.
        if urut and re.match(r"^[A-Z]\.\s", teks) and len(teks) < 60:
            x.paragraph_format.space_before = Pt(JARAK_ANTAR_BAB_PT)
        for r in x.runs:
            r.font.name = "Arial"
            if r.font.size is not None and r.font.size < Pt(12):
                r.font.size = Pt(12)


# ── LHPemantauan (pemantauan-umum) ───────────────────────────────────────────
# Bab "Ringkasan Status" DIBUANG atas keputusan auditor (27 Agu 2026). Bab itu
# menghitung field `status`/`target`/`realisasi` yang tidak pernah ditulis siapa
# pun — hasilnya selalu "0 HIJAU, 0 KUNING, 0 MERAH" sementara bab berikutnya
# menampilkan item berstatus KUNING, dua bab saling menyangkal. Menambalnya
# menuntut medan isian baru di formulir KKSA dan panel sunting temuan; auditor
# memilih laporan langsung masuk ke Hasil Pemantauan saja.

def _blok_hasil_pemantauan(folder: Path) -> list[tuple] | None:
    """F — narasi per item tulisan Ketua Tim. TANPA rekomendasi (itu bab G)."""
    narasi = safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}
    catatan = narasi.get("catatan") or []
    if not catatan:
        return None
    blok: list[tuple] = []
    pengantar = str(narasi.get("pengantar_hasil") or "").strip()
    for b in _daftar(pengantar):
        blok.append(("p", b, False))
    for i, c in enumerate(catatan, 1):
        blok.append(("p", f"{i}. {str(c.get('judul') or f'Item {i}').strip()}", True))
        for b in _daftar(c.get("narasi")):
            blok.append(("p", b, False))
        for t in (c.get("tabel") or []):
            blok.append(("tabel", str(t.get("judul") or "").strip(),
                         list(t.get("kolom") or []), list(t.get("baris") or [])))
    return blok


def _susun_lhpemantauan(docx_path: Path, folder: Path, ruang_lingkup: str) -> list[str]:
    """Susun isi LHPemantauan. Return daftar peringatan."""
    from app.lhr_narasi import _parse_context

    ctx = _parse_context(folder / "context.md")
    doc = Document(str(docx_path))
    warn: list[str] = []

    periode = (ctx.get("periode") or "").strip().rstrip(".")
    blok_periode = None
    if periode:
        awalan = ("Pemantauan dilaksanakan terhitung mulai tanggal "
                  if periode[:1].isdigit() else "Pemantauan dilaksanakan ")
        blok_periode = [("p", f"{awalan}{periode}.", False)]

    metodologi = str(ctx.get("metodologi") or "").strip() or (
        "Pemantauan dilaksanakan melalui penelaahan dokumen kemajuan pelaksanaan, "
        "konfirmasi kepada pihak terkait, serta pembandingan realisasi terhadap target "
        "yang ditetapkan. Pemantauan tidak memberikan opini keyakinan dan hanya "
        "menyampaikan informasi status pelaksanaan berdasarkan data yang tersedia.")

    isi = [
        ("{{B_TUJUAN_LINGKUP}}", _blok_tujuan_lingkup(ctx, ruang_lingkup)),
        ("{{C_PERIODE_PEMANTAUAN}}", blok_periode),
        ("{{D_METODOLOGI_PEMANTAUAN}}", [("p", metodologi, False)]),
        ("{{E_HASIL_PEMANTAUAN}}", _blok_hasil_pemantauan(folder)),
        ("{{F_REKOM}}", _blok_rekomendasi_evaluasi(folder)),
    ]
    for penanda, blok in isi:
        nama = penanda.strip("{}")
        if not blok:
            warn.append(f"{nama} tidak terisi (sumber datanya kosong)")
            continue
        if not _isi_penanda_blok(doc, penanda, blok):
            warn.append(f"{nama} gagal disusun (penanda tak ditemukan)")

    _seragamkan(doc, "A.  Dasar", "G.  Apresiasi")
    doc.save(str(docx_path))
    return warn


def _blok_tujuan_lingkup(ctx: dict, ruang_lingkup: str) -> list[tuple] | None:
    """B — tujuan DAN ruang lingkup; sebelumnya hanya tujuan yang muncul."""
    blok: list[tuple] = []
    tujuan = str(ctx.get("tujuan") or "").strip()
    if tujuan:
        blok.append(("p", f"Tujuan pemantauan adalah {_kecilkan_awal(tujuan)}", False))
    rl = (ruang_lingkup or ctx.get("ruang_lingkup") or "").strip()
    if rl:
        blok.append(("p", f"Ruang lingkup pemantauan adalah {_kecilkan_awal(rl)}", False))
    return blok or None


def _isi_penanda_blok(doc, penanda: str, blok: list[tuple]) -> bool:
    """Ganti paragraf berisi `penanda` dengan rangkaian blok."""
    from copy import deepcopy

    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
    from docx.text.paragraph import Paragraph

    sasaran = next((x for x in doc.paragraphs if penanda in x.text), None)
    if sasaran is None:
        return False
    for item in blok:
        if item[0] == "tabel":
            _sisip_tabel(doc, sasaran, item[1], item[2], item[3])
            continue
        baru = deepcopy(sasaran._p)
        sasaran._p.addprevious(baru)
        sal = Paragraph(baru, sasaran._parent)
        _set_para(sal, item[1])
        sal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for r in sal.runs:
            r.bold = item[2]
            r.italic = False
            r.font.name = "Arial"
            r.font.size = Pt(12)
    sasaran._p.getparent().remove(sasaran._p)
    return True


def _susun_lhe(docx_path: Path, folder: Path, skill: str, ruang_lingkup: str) -> list[str]:
    """Susun isi LHE evaluasi-umum. Return daftar peringatan."""
    from app.lhr_narasi import _parse_context

    ctx = _parse_context(folder / "context.md")
    lke = _baca_lke(folder, skill)
    doc = Document(str(docx_path))
    warn: list[str] = []

    isi = [
        ("{{B_TUJUAN_SASARAN}}", _blok_tujuan_sasaran(folder, ctx)),
        ("{{C_RUANG_LINGKUP}}", _blok_ruang_lingkup(ruang_lingkup or ctx.get("ruang_lingkup") or "")),
        ("{{D_METODOLOGI}}", _blok_metodologi(ctx)),
        ("{{E_HASIL}}", _blok_hasil_evaluasi(folder, lke)),
        ("{{F_REKOMENDASI}}", _blok_rekomendasi_evaluasi(folder)),
    ]
    for penanda, blok in isi:
        nama = penanda.strip("{}")
        if not blok:
            warn.append(f"{nama} tidak terisi (sumber datanya kosong)")
            continue
        if not _isi_penanda_blok(doc, penanda, blok):
            warn.append(f"{nama} gagal disusun (penanda tak ditemukan)")

    _seragamkan(doc, "A.  Dasar", "G.  Apresiasi")
    doc.save(str(docx_path))
    return warn


def _tulis_ulang_rekomendasi(docx_path: Path, folder: Path) -> bool:
    """Bab Rekomendasi memuat rekomendasinya saja, tanpa mengulang judul temuan.

    V6 mencetak "T-001. <judul temuan>" sebagai kepala tiap butir, sehingga bab
    Rekomendasi terbaca seperti pengulangan bab Hasil Audit. LHA Inspektorat II
    yang sesungguhnya langsung menomori rekomendasinya.
    """
    from copy import deepcopy

    from docx.text.paragraph import Paragraph

    rek = safe_read_json(folder / "_LHP" / "rekomendasi.json") or {}
    kkp = safe_read_json(folder / "_KKP" / "temuan.json") or {}
    butir: list[str] = []
    for t in (kkp.get("temuan") or []):
        nilai = rek.get(str(t.get("id_temuan") or ""))
        if isinstance(nilai, dict):
            nilai = nilai.get("rekomendasi")
        nilai = str(nilai or "").strip()
        if nilai:
            butir.append(nilai)
    if not butir:
        return False

    doc = Document(str(docx_path))
    par = doc.paragraphs
    awal = next((k for k, x in enumerate(par)
                 if x.text.strip().startswith("Berdasarkan hasil audit, Tim merekomendasikan")),
                None)
    akhir = next((k for k in range(awal + 1, len(par))
                  if par[k].text.strip() == "BAB V"), None) if awal is not None else None
    if awal is None or akhir is None:
        return False
    donor = par[awal]
    for i, teks in enumerate(butir, 1):
        baru = deepcopy(donor._p)
        par[akhir]._p.addprevious(baru)
        salinan = Paragraph(baru, donor._parent)
        _set_para(salinan, f"{i}. {teks}")
        for r in salinan.runs:
            r.bold = False
            r.italic = False
    for k in range(awal + 1, akhir):
        par[k]._p.getparent().remove(par[k]._p)
    doc.save(str(docx_path))
    return True


def _awali_ruang_lingkup(docx_path: Path) -> bool:
    """Bab Ruang Lingkup dibuka "Ruang lingkup audit adalah ..." (arahan auditor)."""
    doc = Document(str(docx_path))
    par = doc.paragraphs
    i = next((k for k, x in enumerate(par)
              if x.text.strip() == "Ruang Lingkup Audit"), None)
    if i is None or i + 1 >= len(par):
        return False
    isi = par[i + 1].text.strip()
    if not isi or isi.lower().startswith("ruang lingkup"):
        return False
    _set_para(par[i + 1], f"Ruang lingkup audit adalah {_kecilkan_awal(isi)}")
    doc.save(str(docx_path))
    return True


def _hentikan_kop(docx_path: Path) -> bool:
    """Kop hanya di Nota Dinas dan halaman sampul, tidak di halaman isi.

    Templat sudah memutus tautan header pada seksi isi, tetapi pemutus itu
    menempel pada paragraf penanda yang DIBUANG perender — ikut hilang, sehingga
    kop terbawa sampai halaman terakhir. Dipasang ulang di sini.
    """
    doc = Document(str(docx_path))
    if len(doc.sections) < 3:
        return False
    ubah = False
    for sec in doc.sections[2:]:
        if sec.header.is_linked_to_previous:
            sec.header.is_linked_to_previous = False
            for par in sec.header.paragraphs:
                _set_para(par, "")
            ubah = True
    if ubah:
        doc.save(str(docx_path))
    return ubah


def _betulkan_periode(docx_path: Path, folder: Path) -> bool:
    """Isi bab Periode pada laporan pemantauan dari context.md.

    V6 membacanya dari `ctx["periode_pelaksanaan"]`, padahal pembaca context.md
    di V6 memetakan "Periode Pelaksanaan" ke kunci `periode` — jadi kunci yang
    dicari itu TIDAK PERNAH ada dan bab Periode selalu terbit sebagai penanda
    kosong. Diperbaiki di sini karena V6 baca-saja. (Ditemukan 27 Agu 2026 dari
    laporan contoh pemantauan-umum.)
    """
    from app.lhr_narasi import _parse_context

    periode = (_parse_context(folder / "context.md").get("periode") or "").strip()
    if not periode:
        return False
    doc = Document(str(docx_path))
    n = 0
    for par in doc.paragraphs:
        if par.text.strip().startswith("[DIISI — Periode"):
            _set_para(par, periode)
            for r in par.runs:
                r.italic = False
            n += 1
    if n:
        doc.save(str(docx_path))
    return bool(n)


# ── Ringkasan Eksekutif & Dasar Hukum LHR reviu-rka-kl (lapisan app) ──────────
# Template LHR reviu-rka-kl memuat dua penanda yang TIDAK dikenal V6:
# {{RINGKASAN_EKSEKUTIF}} dan {{DASAR_HUKUM_LIST}}. V6 melewatkannya apa adanya;
# keduanya diisi di sini SETELAH render, memakai data yang SAMA dengan badan
# laporan (temuan yang disetujui + rekomendasi) supaya Ringkasan tidak memuat
# temuan yang sudah ditolak auditor. Bentuk mengikuti contoh LHR Inspektorat II:
# Arial 12, spasi 1,5, rata kiri-kanan.
_DASAR_HUKUM_BAKU = (
    "Peraturan Pemerintah Nomor 60 Tahun 2008 tentang Sistem Pengendalian Intern Pemerintah.",
    "Peraturan Menteri Keuangan Nomor 107 Tahun 2024 tentang Perubahan atas Peraturan "
    "Menteri Keuangan Nomor 62 Tahun 2023 tentang Perencanaan Anggaran, Pelaksanaan "
    "Anggaran, serta Akuntansi dan Pelaporan Keuangan.",
    "Peraturan Menteri Keuangan Nomor 41 Tahun 2026 tentang Perubahan Kedua atas "
    "Peraturan Menteri Keuangan Nomor 62 Tahun 2023.",
)


def _dedup_urut(seq) -> list[str]:
    keluar, terlihat = [], set()
    for x in seq:
        x = str(x or "").strip()
        if x and x not in terlihat:
            terlihat.add(x)
            keluar.append(x)
    return keluar


def _isi_penanda_paragraf(doc, token: str, baris: list[tuple]) -> bool:
    """Ganti paragraf ber-`token` dengan beberapa paragraf (Arial 12/1,5/justify).

    `baris` = list of (teks, bold).
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Pt

    anchor = next((p for p in doc.paragraphs if token in p.text), None)
    if anchor is None:
        return False
    for teks, tebal in baris:
        par = anchor.insert_paragraph_before(style=anchor.style)
        pf = par.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.line_spacing = 1.5
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        run = par.add_run(teks)
        run.bold = tebal
        run.font.name = "Arial"
        run.font.size = Pt(12)
        rpr = run._element.get_or_add_rPr()
        rf = rpr.find(qn("w:rFonts"))
        if rf is None:
            rf = OxmlElement("w:rFonts")
            rpr.append(rf)
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rf.set(qn(a), "Arial")
    anchor._element.getparent().remove(anchor._element)
    return True


def _isi_setelah_judul(doc, judul: str, baris: list[tuple]) -> bool:
    """Sisipkan paragraf TEPAT SETELAH sebuah judul bab. Return berhasil?

    Dipakai bila penanda `{{...}}` sudah lenyap sebelum lapisan app sempat
    mengisinya. V6 punya jaring pengaman yang MENGOSONGKAN sejumlah penanda
    (RINGKASAN_EKSEKUTIF, H_APRESIASI, E_GAMBARAN_UMUM) tepat sebelum menyimpan
    berkas — niatnya baik (jangan ada `{{...}}` mentah di laporan), tapi
    akibatnya bab Ringkasan Eksekutif terbit KOSONG karena penandanya sudah
    hilang saat kita mencarinya. Menyandar pada judul bab kebal terhadap itu.
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.shared import Pt

    kepala = next((x for x in doc.paragraphs if x.text.strip() == judul), None)
    if kepala is None:
        return False
    sesudah = kepala
    for teks, tebal in baris:
        par = sesudah.insert_paragraph_before(style=kepala.style)
        # insert_paragraph_before menyisipkan SEBELUM `sesudah`; supaya urutannya
        # benar, pindahkan elemen baru ke posisi tepat setelah paragraf terakhir.
        kepala._element.addnext(par._element) if sesudah is kepala else             sesudah._element.addnext(par._element)
        pf = par.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.line_spacing = 1.5
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        run = par.add_run(teks)
        run.bold = tebal
        run.font.name = "Arial"
        run.font.size = Pt(12)
        sesudah = par
    return True


def _kumpulkan_ringkasan_rkakl(folder: Path, anotasi: dict) -> tuple[list[str], list[str]]:
    """Judul catatan (temuan DISETUJUI) + teks rekomendasi untuk Ringkasan Eksekutif.

    Menghormati keputusan HITL: temuan ber-status REJECTED dibuang dan koreksi
    judul auditor diterapkan — sama seperti yang dipakai saat merender badan
    laporan, supaya Ringkasan tidak menyebut temuan yang sudah ditolak.
    """
    data = safe_read_json(folder / "_KKP" / "temuan.json") or {}
    temuan = data.get("temuan") or []
    judul_catatan: list[str] = []
    id_dipakai: list[str] = []
    for t in temuan:
        if not isinstance(t, dict):
            continue
        tid = t.get("id_temuan")
        a = (anotasi or {}).get(tid) or {}
        if str(a.get("status") or "").upper() == "REJECTED":
            continue
        edits = a.get("edits") or {}
        judul = (edits.get("judul_temuan") or edits.get("judul")
                 or t.get("judul_temuan") or t.get("judul") or "").strip()
        if judul:
            judul_catatan.append(judul)
            id_dipakai.append(tid)
    rek = safe_read_json(folder / "_LHP" / "rekomendasi.json") or {}
    rekom_texts: list[str] = []
    if isinstance(rek, dict):
        for tid in id_dipakai:
            nilai = rek.get(tid)
            if isinstance(nilai, dict):
                nilai = nilai.get("rekomendasi")
            if str(nilai or "").strip():
                rekom_texts.append(str(nilai).strip())
    return _dedup_urut(judul_catatan), _dedup_urut(rekom_texts)


def _blok_ringkasan_rkakl(judul: str, catatan: list[str], rekom: list[str]) -> list[tuple]:
    blok = [
        ("RKA-K/L adalah dokumen rencana keuangan tahunan Kementerian/Lembaga yang "
         "disusun menurut Bagian Anggaran Kementerian/Lembaga.", False),
        (f"Inspektorat II melakukan {judul} untuk memberikan keyakinan terbatas "
         "(limited assurance) atas kesesuaian penyusunan anggaran terhadap kaidah "
         "penganggaran yang berlaku.", False),
    ]
    if catatan:
        blok.append(("Berdasarkan hasil reviu, dapat disimpulkan bahwa sebagian dokumen "
                     "TOR yang disusun belum sesuai format, dengan catatan sebagai berikut:",
                     False))
        blok += [("•  " + c, False) for c in catatan]
        if rekom:
            blok.append(("Inspektorat II merekomendasikan perbaikan sebagai berikut:", False))
            blok += [(f"{i}. {r}", False) for i, r in enumerate(rekom, 1)]
    else:
        blok.append(("Berdasarkan hasil reviu secara terbatas, tidak terdapat hal-hal yang "
                     "membuat kami yakin bahwa perencanaan anggaran tidak disusun sesuai "
                     "dengan kaidah penganggaran yang berlaku.", False))
    return blok


def _blok_dasar_hukum_rkakl(nomor_st: str, tanggal_st: str, nota_dinas: str) -> list[tuple]:
    items = list(_DASAR_HUKUM_BAKU)
    if str(nota_dinas or "").strip():
        items.append(str(nota_dinas).strip().rstrip(".") + ".")
    if str(nomor_st or "").strip():
        st = f"Surat Tugas Inspektur II Nomor {nomor_st}"
        if str(tanggal_st or "").strip():
            st += f" tanggal {tanggal_st}"
        items.append(st.rstrip(".") + ".")
    return [(f"{i}. {x}", False) for i, x in enumerate(items, 1)]


def _temuan_disetujui_rkakl(folder: Path, anotasi: dict) -> list[dict]:
    """Temuan yang DISETUJUI (REJECTED dibuang, koreksi auditor diterapkan)."""
    data = safe_read_json(folder / "_KKP" / "temuan.json") or {}
    hasil: list[dict] = []
    for t in data.get("temuan") or []:
        if not isinstance(t, dict):
            continue
        a = (anotasi or {}).get(t.get("id_temuan")) or {}
        if str(a.get("status") or "").upper() == "REJECTED":
            continue
        hasil.append({**t, **(a.get("edits") or {})})
    return hasil


def _teks_gabung(nilai) -> str:
    """Rangkai field yang bisa berupa list ATAU teks berbaris jadi satu kalimat."""
    if isinstance(nilai, list):
        return " ".join(str(x).strip() for x in nilai if str(x).strip())
    return str(nilai or "").strip()


def _seragamkan_badan_rkakl(doc, dari: str, sampai: str) -> int:
    """Samakan bentuk badan LHR: Arial 12, rata kiri-kanan, spasi 1,5.

    Butir bab Rekomendasi terbit Arial 10 rata kiri karena pembangunnya di V6
    menyetel `size: 10` dan tidak menyetel perataan; beberapa isi bab lain juga
    tidak ber-perataan. Diseragamkan di sini karena V6 baca-saja. Ketebalan
    (bold) TIDAK diubah — judul dan sub-judul tetap tebal.
    """
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
    from docx.shared import Pt

    par = doc.paragraphs
    i = next((k for k, x in enumerate(par) if x.text.strip() == dari), None)
    j = next((k for k, x in enumerate(par) if x.text.strip() == sampai), None)
    if i is None or j is None or j < i:
        return 0
    n = 0
    for x in par[i:j + 1]:
        if not x.text.strip():
            continue
        pf = x.paragraph_format
        pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        pf.line_spacing = 1.5
        pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
        for r in x.runs:
            r.font.name = "Arial"
            r.font.size = Pt(12)
        n += 1
    return n


def _aspek_tak_tersimpulkan(folder: Path) -> list[dict]:
    """Aspek berkesimpulan TIDAK_CUKUP_DATA di kertas kerja.

    Aspek semacam ini TIDAK menghasilkan temuan, sehingga tanpa penanganan
    khusus ia lenyap dari laporan — padahal justru itu batas cakupan reviu.
    Terbukti pada penugasan RKA-K/L nyata: 4 dari 9 aspek tidak dapat
    disimpulkan, dua di antaranya (konsistensi TOR-RAB dan kewajaran biaya)
    adalah inti sasaran penugasan, dan laporan sama sekali tidak menyebutnya.
    Simpulan pun berbunyi seolah reviu tuntas. (Ditemukan 30 Agu 2026.)
    """
    d = safe_read_json(folder / "_KKP" / "penilaian-aspek.json") or {}
    rows = d.get("aspek") if isinstance(d, dict) else None
    return [r for r in (rows or [])
            if isinstance(r, dict)
            and str(r.get("kesimpulan") or "").strip().upper() == "TIDAK_CUKUP_DATA"
            and str(r.get("aspek") or "").strip()]


def _blok_batas_cakupan(aspek: list[dict]) -> list[tuple]:
    """Bagian penutup Uraian Hasil Reviu: aspek yang belum dapat disimpulkan."""
    if not aspek:
        return []
    n = len(aspek)
    blok: list[tuple] = [
        (f"Terdapat {n} ({_terbilang(n)}) aspek yang belum dapat disimpulkan dalam "
         f"reviu ini karena keterbatasan data, dengan uraian sebagai berikut:", False),
    ]
    for i, r in enumerate(aspek, 1):
        nama = str(r.get("aspek") or "").strip()
        blok.append((f"{i}. {nama}", True))
        dasar = _teks_gabung(r.get("dasar"))
        if dasar:
            blok.append((dasar, False))
    blok.append(("Keterbatasan tersebut merupakan batas cakupan reviu: atas aspek-aspek "
                 "di atas, Inspektorat II tidak memberikan keyakinan apa pun.", False))
    return blok


def _blok_hasil_reviu_rkakl(temuan: list[dict]) -> list[tuple]:
    """Uraian Hasil Reviu — daftar catatan LANGSUNG, tanpa pengelompokan aspek.

    Tiap catatan dirangkai mengalir dari unsur K/K/S/A kertas kerja. Rekomendasi
    TIDAK dimasukkan di sini (disusun di bab Rekomendasi tersendiri).
    """
    if not temuan:
        return [("Berdasarkan hasil reviu, tidak terdapat catatan yang perlu "
                 "ditindaklanjuti.", False)]
    blok: list[tuple] = [
        (f"Berdasarkan hasil reviu, tim reviu menyampaikan {len(temuan)} catatan "
         "sebagai berikut:", False)
    ]
    for i, t in enumerate(temuan, 1):
        judul = (_teks_gabung(t.get("judul_temuan")) or _teks_gabung(t.get("judul"))
                 or f"Catatan {i}")
        blok.append((f"{i}. {judul}", True))
        kondisi = _teks_gabung(t.get("kondisi"))
        if kondisi:
            blok.append((kondisi, False))
        kriteria = _teks_gabung(t.get("kriteria"))
        if kriteria:
            blok.append(("Kondisi tersebut tidak sesuai dengan: " + kriteria, False))
        sebab = _teks_gabung(t.get("sebab"))
        if sebab:
            if sebab.lower().startswith(("tidak ", "belum ")):
                blok.append((sebab if sebab.endswith(".") else sebab + ".", False))
            else:
                blok.append((f"Hal tersebut disebabkan {_kecilkan_awal(sebab)}", False))
        akibat = _teks_gabung(t.get("akibat"))
        if akibat:
            blok.append((f"Hal tersebut mengakibatkan {_kecilkan_awal(akibat)}", False))
    return blok


def _betulkan_rkakl(docx_path: Path, folder: Path, gambaran_umum: str,
                    args: dict | None = None, catatan_judul: list[str] | None = None,
                    rekom_texts: list[str] | None = None,
                    temuan_disetujui: list[dict] | None = None) -> list[str]:
    """Tambal cacat reviu-rka-kl + isi Ringkasan Eksekutif & Dasar Hukum. Return peringatan."""
    peringatan: list[str] = []
    doc = Document(str(docx_path))
    berubah = False
    args = args or {}
    peringatan: list[str] = []

    # Ringkasan Eksekutif & Dasar Hukum — penanda app di luar pengetahuan V6.
    from app.lhr_narasi import _parse_context
    ctx = _parse_context(folder / "context.md")
    judul = (args.get("judul") or "Reviu RKA-K/L").strip()
    blok_re = _blok_ringkasan_rkakl(judul, catatan_judul or [], rekom_texts or [])
    if _isi_penanda_paragraf(doc, "{{RINGKASAN_EKSEKUTIF}}", blok_re):
        berubah = True
    elif _isi_setelah_judul(doc, "Ringkasan Eksekutif", blok_re):
        # V6 mengosongkan penanda RINGKASAN_EKSEKUTIF sebagai jaring pengaman
        # sebelum menyimpan, jadi penandanya kerap sudah hilang di sini.
        berubah = True
    else:
        peringatan.append("WARNING:Ringkasan Eksekutif gagal diisi (penanda maupun "
                          "judul babnya tidak ditemukan)")
    nota = (args.get("dasar_permintaan") or ctx.get("dasar") or "").strip()
    if _isi_penanda_paragraf(
        doc, "{{DASAR_HUKUM_LIST}}",
        _blok_dasar_hukum_rkakl(ctx.get("nomor_st") or "", ctx.get("tanggal_st") or "", nota),
    ):
        berubah = True

    # Uraian Hasil Reviu — daftar catatan LANGSUNG (tanpa pengelompokan aspek C1–C6).
    # Penanda dulu; bila V6 sudah mengosongkannya, sandar pada judul bab.
    aspek_buntu = _aspek_tak_tersimpulkan(folder)
    blok_hasil = (_blok_hasil_reviu_rkakl(temuan_disetujui or [])
                  + _blok_batas_cakupan(aspek_buntu))
    if _isi_penanda_paragraf(doc, "{{HASIL_REVIU_LIST}}", blok_hasil):
        berubah = True
    elif _isi_setelah_judul(doc, "Uraian Hasil Reviu", blok_hasil):
        berubah = True
    else:
        peringatan.append("WARNING:Uraian Hasil Reviu gagal diisi (penanda maupun "
                          "judul babnya tidak ditemukan)")

    # Simpulan tidak boleh berbunyi seolah reviu tuntas bila ada aspek yang
    # belum dapat disimpulkan — itu memberi keyakinan yang tidak pernah diperoleh.
    if aspek_buntu:
        n = len(aspek_buntu)
        for par in doc.paragraphs:
            t = par.text.strip()
            if t.startswith("Berdasarkan reviu yang telah dilaksanakan") and t.endswith("."):
                _set_para(par, t[:-1] + (
                    f", serta {n} ({_terbilang(n)}) aspek yang belum dapat disimpulkan "
                    f"karena keterbatasan data sebagaimana diuraikan pada bab Uraian "
                    f"Hasil Reviu. Atas aspek-aspek tersebut Inspektorat II tidak "
                    f"memberikan keyakinan."))
                berubah = True
                break

    # Gambaran Umum: V6 membacanya dari `gambaran_umum_rkakl` yang tak pernah
    # ditulis siapa pun, sementara tulisan agen KT terbuang percuma.
    for par in doc.paragraphs:
        if par.text.strip().startswith("[DIISI — Gambaran umum RKA-K/L") and gambaran_umum:
            _set_para(par, gambaran_umum)
            for r in par.runs:
                r.italic = False
            berubah = True
            break

    # Keyakinan palsu C1–C6: hanya diganti bila memang ADA temuan yang tak
    # terklasifikasi. Bila tidak ada temuan sama sekali, kalimat afirmatifnya sah.
    try:
        temuan = json.loads((folder / "_KKP" / "temuan.json")
                            .read_text(encoding="utf-8")).get("temuan") or []
    except (OSError, ValueError):
        temuan = []
    tanpa_area = temuan and not any(str(t.get("area") or "").strip() for t in temuan)
    if tanpa_area:
        n = 0
        for par in doc.paragraphs:
            if par.text.strip() in _KLAIM_RKAKL:
                _set_para(par, _TANPA_KLASIFIKASI)
                n += 1
        if n:
            berubah = True
            peringatan.append(
                f"WARNING:{n} sub-bab aspek RKA-K/L tidak dapat disimpulkan — "
                f"{len(temuan)} temuan tidak punya field `area` (c1..c6). Isi `area` "
                f"tiap temuan lalu render ulang.")


    # {{TAHUN_PKPT}} di surat pengantar tidak dikenali siapa pun sehingga tercetak
    # mentah. Diisi dari tahun anggaran penugasan, atau tahun pada tanggal ST.
    tahun = str(ctx.get("tahun_anggaran") or "").strip()
    if not tahun:
        m_th = re.search(r"(20\d{2})", str(ctx.get("tanggal_st") or ""))
        tahun = m_th.group(1) if m_th else ""
    for par in doc.paragraphs:
        if "{{TAHUN_PKPT}}" in par.text:
            if tahun:
                _set_para(par, par.text.replace("{{TAHUN_PKPT}}", tahun))
                berubah = True
            else:
                peringatan.append("WARNING:{{TAHUN_PKPT}} tak bisa diisi — "
                                  "context.md tidak memuat Tahun Anggaran")

    # Bab Metodologi terbit berbunyi "Pemantauan dilaksanakan ..." pada laporan
    # REVIU: V6 memakai pembangun metodologi milik pemantauan untuk jalur ini.
    for par in doc.paragraphs:
        if par.text.strip().startswith("Pemantauan dilaksanakan melalui"):
            _set_para(par, "Reviu dilaksanakan dengan menelaah dokumen Renja dan RKA-K/L "
                           "beserta dokumen pendukungnya, yaitu Kerangka Acuan Kerja (TOR) "
                           "dan Rincian Anggaran Biaya (RAB), serta konfirmasi kepada "
                           "pihak terkait. Reviu memberikan keyakinan terbatas.")
            berubah = True
    # Terakhir: seragamkan bentuk badan laporan (Arial 12 / justify / 1,5).
    if _seragamkan_badan_rkakl(doc, "Ringkasan Eksekutif", "Apresiasi"):
        berubah = True

    if berubah:
        doc.save(str(docx_path))
    return peringatan


def _penanda_tersisa(docx_path: Path) -> list[str]:
    """Penanda {{...}} yang tak terisi pada laporan jadi.

    Jaring pengaman umum untuk ketidakcocokan TEMPLAT vs KODE. Templat dibaca
    dari disk tiap render, sedangkan kode hidup di proses backend — mengubah
    templat tanpa memuat ulang backend membuat laporan terbit dengan penanda
    mentah, dan tidak ada satu pun pesan galat. Terjadi 28 Agu 2026: templat
    RKA-K/L yang baru dipakai backend berkode lama, sehingga LHR terbit berisi
    "{{RE_RKAKL}}" dan kawan-kawan.
    """
    doc = Document(str(docx_path))
    teks = [x.text for x in doc.paragraphs]
    for t in doc.tables:
        for r in t.rows:
            for c in r.cells:
                teks.append(c.text)
    pola = "\\{\\{[A-Z0-9_]+\\}\\}"
    return sorted(set(re.findall(pola, "\n".join(teks))))


async def _render_kksa(folder: Path, args: dict) -> dict:
    """Render LHP paradigma KKSA via render_lhp.py V6 (placeholder {{...}}).

    CATATAN reviu-pengadaan (23 Agu 2026): jalur ini TIDAK berlaku lagi untuk
    skill tersebut. Sub-bab C.1/C.2 sudah digabung jadi `{{C_HASIL_REVIU}}` di
    template, sedangkan V6 (read-only) masih mencari `{{C1_PERENCANAAN}}` dan
    `{{C2_PEMILIHAN}}` — akibatnya bab Hasil Reviu akan terbit KOSONG tanpa
    pesan galat. Lebih baik ditolak terang-terangan di sini.

    Overlay HITL WAJIB diterapkan di sini, sama seperti di render KKP.
    V6 `render_lhp.py` membaca `_KKP/temuan.json` langsung dari disk, sedangkan
    koreksi Anggota Tim hidup di DB (`TemuanReview.edited_fields`) dan status
    REJECTED tidak tercermin di file. Tanpa overlay, laporan tersusun dari teks
    ASLI agen: koreksi auditor hilang dan temuan yang sudah ditolak tetap masuk
    laporan — persis kelas cacat yang tidak boleh ada di produk audit.
    (Ditambahkan 9 Agu 2026; sebelumnya overlay hanya ada di jalur KKP.)
    """
    if _slug(args.get("skill") or "") in ("evaluasi-umum", "pemantauan-umum"):
        if not (safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}).get("catatan"):
            return {"content": [{"type": "text", "text": (
                "FAILED|narasi bab Hasil belum ada. Panggil `write_narasi_laporan` lebih "
                "dulu: `pengantar_hasil` + `catatan` (tiap catatan: `id_temuan` + judul + "
                "`narasi` yang MENGALIR, boleh bertabel). Rekomendasi TIDAK ditulis di sini "
                "— itu bab tersendiri, dari `write_rekomendasi_json`."
            )}], "is_error": True}
        cacat = _periksa_catatan_vs_temuan(folder)
        if cacat:
            return {"content": [{"type": "text", "text": f"FAILED|{cacat}"}], "is_error": True}
    if _slug(args.get("skill") or "") == "audit-umum":
        if not (safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}).get("catatan"):
            return {"content": [{"type": "text", "text": (
                "FAILED|narasi bab Hasil Audit belum ada. Panggil `write_narasi_laporan` "
                "lebih dulu: tiap `catatan` memuat `id_temuan` + judul + `narasi` (uraian "
                "KONDISI, boleh berbutir/kronologis) + `kriteria` + `sebab` + `akibat`, "
                "dan boleh disertai `tabel` untuk rincian. Susun ulang dari temuan.json — "
                "JANGAN salin mentah satu kolom kertas kerja jadi satu paragraf."
            )}], "is_error": True}
        cacat = _periksa_catatan_vs_temuan(folder)
        if cacat:
            return {"content": [{"type": "text", "text": f"FAILED|{cacat}"}], "is_error": True}

    if _slug(args.get("skill") or "") in ("reviu-pengadaan", "reviu-umum"):
        return {"content": [{"type": "text", "text": (
            "FAILED|skill ini tidak memakai jalur KKSA. Laporannya berupa NARASI di atas "
            "template resmi: panggil `write_narasi_laporan` lalu `render_lhr_narasi"
            "(skill=...)`. Templatenya tidak memuat penanda KKSA, sehingga jalur ini "
            "akan menghasilkan bab Hasil Reviu yang kosong."
        )}], "is_error": True}

    rekomendasi = folder / "_LHP" / "rekomendasi.json"
    if not rekomendasi.exists():
        return {"content": [{"type": "text", "text": "FAILED|rekomendasi.json belum ada"}], "is_error": True}
    skill = args.get("skill") or ""
    # B — bab Gambaran Umum tidak boleh kosong/placeholder; paksa agen mengisinya.
    gu = (args.get("gambaran_umum") or "").strip()
    if not gu or gu.upper().startswith("[DIISI"):
        return {
            "content": [{
                "type": "text",
                "text": "FAILED|gambaran_umum kosong/placeholder. Susun 3–5 kalimat substantif "
                        "(obyek, nilai anggaran/HPS, mekanisme/periode) dari KP+PKP+digest+context, lalu render ulang.",
            }],
            "is_error": True,
        }
    template = resolve_lhp_template(skill)
    if template is None:
        return {
            "content": [{
                "type": "text",
                "text": f"FAILED|template LHP tidak ada untuk skill='{skill}' (cek APP_TEMPLATES_PATH/_skeleton-lhp/)",
            }],
            "is_error": True,
        }
    # Terapkan overlay HITL (koreksi AT + buang REJECTED) sebelum V6 membaca
    # temuan.json, lalu SELALU pulihkan file aslinya di finally — pola yang sama
    # dengan render KKP supaya temuan versi agen tidak hilang permanen.
    from app.tools.kkp_tools import (
        _filter_temuan_by_review,
        _restore_temuan_from_backup,
    )

    backup, stats = await _filter_temuan_by_review(folder)
    try:
        # Bersarang di dalam overlay HITL: backup penyambungan memotret keadaan
        # SESUDAH overlay, jadi pemulihannya harus lebih dulu (urutan terbalik)
        # supaya temuan.json kembali persis seperti semula.
        sambung = _sambung_data_terpisah(folder)
        try:
            code, out, err = await run_v6_script(
                "scripts/render_lhp.py",
                [
                    "--penugasan", str(folder),
                    "--rekomendasi-file", str(rekomendasi),
                    "--template", str(template),
                    "--judul", args["judul"],
                    "--auditi", args["auditi"],
                    "--dasar-permintaan", args["dasar_permintaan"],
                    "--gambaran-umum", args["gambaran_umum"],
                    "--tanggal-exit-meeting", args.get("tanggal_exit_meeting", "") or "",
                ],
                timeout=120,
            )
        finally:
            _restore_temuan_from_backup(folder, sambung)
    finally:
        _restore_temuan_from_backup(folder, backup)

    if code != 0:
        return {"content": [{"type": "text", "text": f"FAILED|exit={code}|err={err[:400]}"}], "is_error": True}
    # Bab D: ganti daftar centang V6 dengan narasi. Kegagalan JANGAN ditelan —
    # tanpa penanaman ini bab D terbit sebagai placeholder "[DIISI ...]".
    warn_d = ""
    if _slug(skill) == "audit-umum":
        outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"),
                      key=lambda f: f.stat().st_mtime)
        if outs:
            if not _tulis_ulang_hasil_audit(outs[-1], folder):
                warn_d += "|WARNING:bab Hasil Audit gagal ditulis ulang (penanda tak ditemukan)"
            if not _tulis_ulang_rekomendasi(outs[-1], folder):
                warn_d += "|WARNING:bab Rekomendasi gagal ditulis ulang"
            _awali_ruang_lingkup(outs[-1])
            _hentikan_kop(outs[-1])

    if _slug(skill) == "evaluasi-umum":
        outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"),
                      key=lambda f: f.stat().st_mtime)
        if outs:
            from app.lhr_narasi import _parse_context
            rl = (args.get("ruang_lingkup")
                  or _parse_context(folder / "context.md").get("ruang_lingkup") or "")
            for pesan in _susun_lhe(outs[-1], folder, skill, rl):
                warn_d += f"|WARNING:{pesan}"

    if _slug(skill) == "pemantauan-umum":
        outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"),
                      key=lambda f: f.stat().st_mtime)
        if outs:
            from app.lhr_narasi import _parse_context
            rl = (args.get("ruang_lingkup")
                  or _parse_context(folder / "context.md").get("ruang_lingkup") or "")
            for pesan in _susun_lhpemantauan(outs[-1], folder, rl):
                warn_d += f"|WARNING:{pesan}"
    elif _slug(skill).startswith("pemantauan"):
        outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"),
                      key=lambda f: f.stat().st_mtime)
        if outs and not _betulkan_periode(outs[-1], folder):
            warn_d += ("|WARNING:bab Periode tidak terisi — pastikan context.md memuat "
                       "\"Periode Pelaksanaan\".")

    if _slug(skill) == "reviu-rka-kl":
        outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"),
                      key=lambda f: f.stat().st_mtime)
        if outs:
            from app.tools.kkp_tools import load_hitl_annotations
            anotasi = await load_hitl_annotations(folder)
            catatan_judul, rekom_texts = _kumpulkan_ringkasan_rkakl(folder, anotasi)
            temuan_disetujui = _temuan_disetujui_rkakl(folder, anotasi)
            for pesan in _betulkan_rkakl(outs[-1], folder,
                                         args.get("gambaran_umum") or "", args,
                                         catatan_judul, rekom_texts, temuan_disetujui):
                warn_d += f"|{pesan}"

    outs = sorted((folder / "_LHP").glob("LHP-SUBSTANSI*.docx"),
                  key=lambda f: f.stat().st_mtime)
    if outs:
        sisa = _penanda_tersisa(outs[-1])
        if sisa:
            warn_d += (f"|WARNING:penanda belum terisi di laporan: {', '.join(sisa)}. "
                       f"Biasanya templat dan kode tidak sepadan — muat ulang backend, "
                       f"atau lengkapi data sumbernya.")

    # A1: sesuaikan judul/kata + nama file per jenis (LHA/LHR/LHE/LP).
    final_name = _finalize_jenis(folder, skill)
    tail = f"|file={final_name}" if final_name else ""
    # Laporkan ke agen KT apa yang dipakai: berapa temuan ditolak & berapa yang
    # memuat koreksi auditor. Angka ini jadi bahan cek silang KT, bukan hiasan.
    hitl = ""
    if stats:
        hitl = (
            f"|hitl=dipakai:{stats['n_included']}/{stats['n_total']}"
            f",ditolak:{stats['n_rejected']}"
            f",koreksi_auditor_diterapkan:{stats['n_edits_applied']}"
        )
    return {"content": [{"type": "text", "text": f"OK|format=kksa|template={template.name}{tail}{hitl}{warn_d}|{out[:120]}"}]}


@tool(
    "render_report",
    "Render laporan hasil sesuai PROFIL FORMAT skill (otomatis): 'kksa' (reviu/audit → "
    "LHP KKSA via V6), 'memo' (Konsultansi → Memo pendapat/saran, butuh _LHP/saran.json), "
    "'rb-4dim' (Eval RB → tabel 4-dimensi, butuh _LHP/penilaian-rb.json). Pakai tool ini "
    "sebagai jalur utama penyusunan laporan untuk SEMUA skill (kksa/memo/rb-4dim/pendampingan).",
    {
        "penugasan_folder": str, "skill": str, "judul": str, "auditi": str,
        "dasar_permintaan": str, "gambaran_umum": str, "tanggal_exit_meeting": str,
    },
)
async def render_report(args: dict) -> dict:
    from app.format_registry import format_profile

    folder = Path(args["penugasan_folder"])
    skill = args.get("skill") or ""
    profile = format_profile(skill)
    if profile == "memo":
        return _render_memo(folder, args)
    if profile == "rb-4dim":
        return _render_rb(folder, args)
    if profile == "pendampingan":
        return _render_pendampingan(folder, args)
    return await _render_kksa(folder, args)


# =============================================================================
# JALUR BARU (13 Agu 2026) — LHR gaya NARASI untuk reviu-pengadaan
#
# Berdampingan dengan `render_report`, TIDAK menggantikannya. Berkas keluaran
# bernama LHR-NARASI-*.docx sehingga laporan gaya lama tidak pernah tertimpa.
# Kalau gaya ini dinilai tidak cocok, cukup berhenti memakainya.
# Lihat app/lhr_narasi.py untuk dasar formatnya.
# =============================================================================


@tool(
    "write_narasi_laporan",
    "Untuk reviu-pengadaan DAN reviu-umum. Tulis _LHP/narasi-laporan.json — bahan "
    "laporan. TIAP isian punya MUARA tetap. reviu-pengadaan: `catatan` -> bab C Hasil "
    "Reviu, `komponen_harga` -> tabel bab B Gambaran Umum, `hal_diperhatikan` -> bab E "
    "Rekomendasi; bab D Simpulan ditulis renderer sendiri (jangan kamu isi). "
    "evaluasi-umum: `pengantar_hasil` + `catatan` -> bab E Hasil Evaluasi, "
    "`hal_diperhatikan` TIDAK dipakai (rekomendasi dari write_rekomendasi_json). "
    "`pengantar_hasil` = rekap keadaan objek + analisisnya SEBELUM daftar temuan "
    "(boleh berbutir; taruh tabel rekap pada `tabel` catatan pertama bila perlu). "
    "Temuan evaluasi ditulis MENGALIR: judul + uraian; JANGAN pakai label "
    "\"Kondisi:/Kriteria:/Sebab:/Akibat:\" — rangkai jadi kalimat. "
    "audit-umum: `catatan` -> bab III Hasil Audit, `hal_diperhatikan` -> bab IV "
    "Rekomendasi. Di audit-umum tiap catatan memakai kerangka LHA: `narasi` = uraian "
    "KONDISI (kronologis, boleh berbutir), lalu `kriteria` (list), `sebab` (list), "
    "`akibat` (kalimat). Renderer yang menambahkan kalimat penyambung \"Kondisi tersebut "
    "tidak sesuai dengan:\" / \"Hal tersebut disebabkan:\" / \"Hal tersebut "
    "mengakibatkan ...\" — kamu JANGAN menulis label itu. Boleh menyertakan `tabel`: "
    "[{judul, kolom:[...], baris:[[...]]}] untuk rincian yang lebih jelas disajikan "
    "sebagai tabel (mis. rincian nilai per pihak). SUSUN ULANG dari temuan.json — "
    "jangan salin mentah satu kolom kertas kerja jadi satu paragraf. "
    "reviu-umum: `catatan` -> bab D Hasil Reviu, `hal_diperhatikan` -> bab E Catatan "
    "dan Rekomendasi (`komponen_harga` TIDAK dipakai). Di reviu-umum, `catatan` WAJIB "
    "memuat SEMUA aspek yang tidak berkesimpulan SESUAI — baik yang TIDAK_SESUAI "
    "(ada temuannya) MAUPUN yang TIDAK_CUKUP_DATA (belum dapat disimpulkan). Aspek "
    "yang belum teruji TIDAK BOLEH hilang dari laporan: pembaca akan menyangka "
    "seluruh sisanya sudah beres. Isi `id_temuan` bila catatan berasal dari temuan, "
    "dan `butir_hasil` pada hal_diperhatikan = nomor urut catatan yang ditindaklanjuti "
    "supaya bab E bisa menunjuk balik ke bab D. "
    "Input: {catatan:[{judul, narasi, jenis}], komponen_harga:[{nama,jumlah,satuan,"
    "nominal}], hal_diperhatikan:[{judul,uraian}]}. `narasi` = PARAGRAF MENGALIR tanpa "
    "label Kondisi/Kriteria/Sebab/Akibat. jenis='catatan' (ada masalah) atau 'positif' "
    "(sasaran terpenuhi). Catatan TIDAK dipilah tahap perencanaan/pemilihan — semua "
    "masuk satu bab C, urut sesuai kamu menuliskannya. JANGAN menyalin mentah dari "
    "temuan.json — susun ulang jadi paragraf utuh.",
    {"penugasan_folder": str, "catatan": list, "komponen_harga": list,
     "hal_diperhatikan": list, "pengantar_hasil": str},
)
async def write_narasi_laporan(args: dict) -> dict:
    """Simpan narasi laporan gaya baru. Kertas kerja AT tidak disentuh.

    Field `narasi` sengaja TERPISAH dari `temuan.json`: kertas kerja adalah
    catatan kerja AT dan tidak boleh ditimpa KT. Laporan punya kebutuhan
    penyajian sendiri (paragraf mengalir, kronologis, bahasa baku APIP) yang
    memang tidak tersedia di kertas kerja.
    """
    folder = Path(args["penugasan_folder"])
    if not folder.exists():
        return {"content": [{"type": "text", "text": f"FAILED|folder tidak ada: {folder}"}],
                "is_error": True}

    catatan_bersih: list[dict] = []
    for c in args.get("catatan") or []:
        if not isinstance(c, dict):
            continue
        narasi = str(c.get("narasi") or "").strip()
        judul = str(c.get("judul") or "").strip()
        if not narasi or not judul:
            continue
        jenis = str(c.get("jenis") or "catatan").lower()
        catatan_bersih.append({
            "judul": judul,
            "narasi": narasi,
            "jenis": "positif" if jenis.startswith("pos") else "catatan",
            "id_temuan": c.get("id_temuan"),
            # Unsur khas LHA (audit-umum). Skill reviu tidak memakainya —
            # narasinya satu paragraf mengalir tanpa kerangka K/K/S/A.
            "kriteria": _daftar(c.get("kriteria")),
            "sebab": _daftar(c.get("sebab")),
            "akibat": str(c.get("akibat") or "").strip(),
            "tabel": [t for t in (c.get("tabel") or [])
                      if isinstance(t, dict) and t.get("kolom") and t.get("baris")],
        })
    if not catatan_bersih:
        return {"content": [{"type": "text",
                             "text": "FAILED|tidak ada catatan valid (butuh judul + narasi)"}],
                "is_error": True}

    data = {
        "schema_version": "narasi-v1",
        # Pengantar bab Hasil (evaluasi-umum): rekap keadaan + analisisnya SEBELUM
        # daftar temuan, mengikuti LHE Inspektorat II.
        "pengantar_hasil": str(args.get("pengantar_hasil") or "").strip(),
        "catatan": catatan_bersih,
        "komponen_harga": [c for c in (args.get("komponen_harga") or []) if isinstance(c, dict)],
        # `butir_hasil` dipertahankan: nomor catatan di bab Hasil Reviu yang
        # ditindaklanjuti butir ini — supaya rekomendasi bisa menunjuk balik ke
        # uraiannya, bukan menggantung tanpa kaitan (keluhan auditor 26 Agu 2026:
        # "nomor 1 2 mana KKSA-nya?").
        "hal_diperhatikan": [h for h in (args.get("hal_diperhatikan") or [])
                             if isinstance(h, dict) and (h.get("uraian") or "").strip()],
    }
    path = folder / "_LHP" / "narasi-laporan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    n_cat = sum(1 for c in catatan_bersih if c["jenis"] == "catatan")
    n_pos = len(catatan_bersih) - n_cat
    return {"content": [{"type": "text", "text":
                         f"OK|catatan={n_cat}|positif={n_pos}|"
                         f"hal_diperhatikan={len(data['hal_diperhatikan'])}|{path.name}"}]}


@tool(
    "render_lhr_narasi",
    "Untuk reviu-pengadaan DAN reviu-umum — WAJIB isi `skill`. Menuang narasi ke "
    "TEMPLATE RESMI (lengkap Nota Dinas, halaman cover, surat pengantar) — isi tetap "
    "narasi mengalir, BUKAN daftar KKSA. Kerangka bab kedua skill SAMA: A Pendahuluan "
    "(latar belakang, dasar, tujuan & sasaran, ruang lingkup, metodologi, jangka waktu, "
    "komposisi tim, standar reviu) · B Gambaran Umum (+ tabel harga bila ada) · "
    "C Hasil Reviu (narasi tiap catatan + placeholder tanggapan Satker) · D Simpulan "
    "(kalimat keyakinan, ditulis renderer — jangan kamu isi) · E Rekomendasi (dari "
    "hal_diperhatikan). Pada reviu-umum, bab C dibuka otomatis dengan kalimat cakupan "
    "aspek dari _KKP/penilaian-aspek.json. Panggil SETELAH write_narasi_laporan. "
    "Keluaran: _LHP/LHR-NARASI-*.docx.",
    {"penugasan_folder": str, "judul": str, "auditi": str, "dasar_permintaan": str,
     "gambaran_umum": str, "skill": str},
)
async def render_lhr_narasi(args: dict) -> dict:
    from app.lhr_narasi import render as _render_narasi

    folder = Path(args["penugasan_folder"])
    if not folder.exists():
        return {"content": [{"type": "text", "text": f"FAILED|folder tidak ada: {folder}"}],
                "is_error": True}
    gu = (args.get("gambaran_umum") or "").strip()
    if not gu or gu.upper().startswith("[DIISI"):
        return {"content": [{"type": "text", "text":
                             "FAILED|gambaran_umum kosong/placeholder. Susun 3–5 kalimat "
                             "substantif (obyek, nilai HPS, metode, periode) lalu render ulang."}],
                "is_error": True}
    cacat = _periksa_catatan_vs_temuan(folder)
    if cacat:
        return {"content": [{"type": "text", "text": f"FAILED|{cacat}"}], "is_error": True}

    try:
        ok, pesan, out = _render_narasi(folder, args)
    except Exception as e:  # noqa: BLE001 — laporkan apa adanya ke agen
        return {"content": [{"type": "text", "text": f"FAILED|render error: {e}"}],
                "is_error": True}
    if not ok:
        return {"content": [{"type": "text", "text": f"FAILED|{pesan}"}], "is_error": True}

    # Cakupan: tiap aspek yang TIDAK berkesimpulan SESUAI harus punya catatannya
    # di bab Hasil Reviu. Kalau kurang, aspek yang belum teruji lenyap dari
    # laporan tanpa jejak — jangan sampai lewat diam-diam.
    warn = ""
    if _slug(args.get("skill") or "") == "reviu-umum":
        from app.lhr_narasi import _aspek

        perlu = sum(1 for r in _aspek(folder)
                    if str(r.get("kesimpulan") or "").strip().upper() != "SESUAI")
        narasi = safe_read_json(folder / "_LHP" / "narasi-laporan.json") or {}
        ada = len(narasi.get("catatan") or [])
        if perlu and ada < perlu:
            warn = (f"|WARNING:bab Hasil Reviu memuat {ada} catatan, padahal {perlu} "
                    f"aspek tidak berkesimpulan SESUAI. Aspek TIDAK_CUKUP_DATA pun "
                    f"wajib dinarasikan.")
    return {"content": [{"type": "text",
                         "text": f"OK|format=narasi|{pesan}|file={out.name}{warn}"}]}


@tool(
    "run_qc_lhp",
    "Jalankan QC SAIPI stage LHP secara SYNCHRONOUS. Memanggil scripts/qc_saipi.py "
    "V6 dengan --stage lhp lalu return status + breakdown severity + excerpt laporan. "
    "Pakai SETELAH render_lhr selesai untuk gate kepatuhan SAIPI tahap pelaporan.",
    {"penugasan_folder": str},
)
async def run_qc_lhp(args: dict) -> dict:
    """Sync version dari QC LHP — ganti pola async marker-flag yang lama
    (`request_qc_lhp` writer flag). Pola lama bermasalah: agen yang memanggilnya
    tidak dapat hasil → improvisasi sendiri.
    """
    folder = Path(args["penugasan_folder"])
    if not folder.exists():
        return {
            "content": [{
                "type": "text",
                "text": f"FAILED|folder penugasan tidak ada: {folder} — cek path (typo?), jangan anggap PASS",
            }],
            "is_error": True,
        }
    code, out, err = await run_v6_script(
        "scripts/qc_saipi.py",
        ["--penugasan", str(folder), "--stage", "lhp"],
        timeout=120,
    )

    # qc_saipi.py exit code: 0=PASS, 2=ada KRITIS (checklist valid), selain itu
    # = ERROR EKSEKUSI → jangan baca checklist basi (bisa "PASS" palsu).
    if code not in (0, 2):
        return {
            "content": [{
                "type": "text",
                "text": (
                    f"FAILED|stage=lhp|qc_saipi gagal dieksekusi (exit={code}) — "
                    f"status QC TIDAK diketahui, JANGAN anggap PASS. err={err[:300]}"
                ),
            }],
            "is_error": True,
        }

    # Sama seperti stage KKP: temuan manual dikecualikan dari LAK-001/LAK-003.
    # Tanpa ini, KT terhalang KRITIS di tahap laporan atas alasan yang sudah
    # sengaja dibebaskan di tahap kertas kerja. Lihat app/qc_exempt.py.
    from app.qc_exempt import terapkan_pengecualian_manual

    pengecualian = terapkan_pengecualian_manual(folder, "lhp")

    checklist = safe_read_json(folder / "_QA-SAIPI" / "checklist-lhp.json")
    total_kritis, total_peringatan, total_needs_review, total_ok = qc_summary_counts(checklist)

    if total_kritis > 0:
        status_label = "BLOCKED_KRITIS"
    elif total_peringatan > 0 or total_needs_review > 0:
        status_label = "PASS_WITH_WARNINGS"
    else:
        status_label = "PASS"

    laporan_path = folder / "_QA-SAIPI" / "laporan-qa-lhp.md"
    laporan_excerpt = ""
    if laporan_path.exists():
        laporan_excerpt = laporan_path.read_text(encoding="utf-8")[:4000]

    catatan_kecuali = ""
    if pengecualian.get("diterapkan"):
        catatan_kecuali = f"|dikecualikan_manual={','.join(pengecualian['dikecualikan'])}"
        if pengecualian.get("tersisa"):
            catatan_kecuali += f"|tetap_kritis={','.join(pengecualian['tersisa'])}"

    return {
        "content": [
            {
                "type": "text",
                "text": (
                    f"stage=lhp|status={status_label}|exit_code={code}|"
                    f"kritis={total_kritis}|peringatan={total_peringatan}|"
                    f"needs_review={total_needs_review}|ok={total_ok}"
                    f"{catatan_kecuali}|"
                    f"laporan_path={laporan_path}\n\n"
                    # Daftar LENGKAP gap lebih dulu — excerpt di bawahnya bisa
                    # terpotong dan menyembunyikan KRITIS (lihat ringkas_gap).
                    f"=== SEMUA GAP (lengkap, dari checklist) ===\n"
                    f"{ringkas_gap(checklist)}\n\n"
                    f"=== LAPORAN QA (excerpt) ===\n{laporan_excerpt}"
                ),
            }
        ]
    }


# =============================================================================
# FORMAT NON-KKSA — Memo Konsultansi + Evaluasi RB (tabel 4-dimensi)
# Renderer MILIK APP (python-docx) — V6 tetap read-only.
# =============================================================================


def _ctx_lines(folder: Path) -> dict:
    """Ambil beberapa field identitas dari context.md (best-effort)."""
    out: dict = {}
    p = folder / "context.md"
    if p.is_file():
        for line in p.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*[-*]?\s*(Kode|Obyek|Nomor ST|Tanggal ST)\s*:\s*(.+)$", line, re.IGNORECASE)
            if m:
                out[m.group(1).strip().lower()] = m.group(2).strip()
    return out


def _render_memo(folder: Path, args: dict) -> dict:
    """Memo Konsultansi: dasar hukum + pertanyaan→pendapat/saran. Tanpa KKSA/keyakinan."""
    saran_path = folder / "_LHP" / "saran.json"
    if not saran_path.exists():
        return {"content": [{"type": "text", "text": "FAILED|_LHP/saran.json belum ada (pakai append_saran)"}], "is_error": True}
    try:
        items = json.loads(saran_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"content": [{"type": "text", "text": f"FAILED|baca saran.json: {e}"}], "is_error": True}
    if not isinstance(items, list) or not items:
        return {"content": [{"type": "text", "text": "FAILED|saran.json kosong"}], "is_error": True}

    ctx = _ctx_lines(folder)
    # Mulai dari template ber-KOP (kop-only) bila tersedia, lalu tambahkan isi
    # memo di bawahnya. Fallback ke dokumen kosong bila template tak ada.
    kop_tpl = settings.templates_path / "_skeleton-lhp" / "template-lhp-konsultansi-umum.docx"
    doc = Document(str(kop_tpl)) if kop_tpl.exists() else Document()
    doc.add_heading("MEMO KONSULTANSI", level=0)
    doc.add_paragraph(args.get("judul") or "Memo Konsultansi")
    meta = doc.add_paragraph()
    meta.add_run(f"Auditan: {args.get('auditi') or ctx.get('obyek', '-')}\n")
    meta.add_run(f"Dasar: {args.get('dasar_permintaan') or ctx.get('nomor st', '-')}\n")
    meta.add_run(f"Kode penugasan: {ctx.get('kode', folder.name)}")
    doc.add_paragraph(
        "Catatan: dokumen ini berisi PENDAPAT/SARAN konsultansi berbasis dasar hukum, "
        "TIDAK memberikan keyakinan, dan TIDAK mengikat pejabat berwenang.",
    ).italic = True

    # Dasar hukum gabungan (unik)
    dh: list[str] = []
    for it in items:
        for d in (it.get("dasar_hukum") or []):
            if d and d not in dh:
                dh.append(d)
    if dh:
        doc.add_heading("Dasar Hukum", level=1)
        for d in dh:
            doc.add_paragraph(d, style="List Bullet")

    doc.add_heading("Pendapat dan Saran", level=1)
    for i, it in enumerate(items, start=1):
        doc.add_heading(f"{i}. {it.get('pertanyaan', '(pertanyaan)')}", level=2)
        if it.get("pendapat"):
            p = doc.add_paragraph(); p.add_run("Pendapat: ").bold = True; p.add_run(str(it["pendapat"]))
        if it.get("saran"):
            p = doc.add_paragraph(); p.add_run("Saran: ").bold = True; p.add_run(str(it["saran"]))

    out_path = folder / "_LHP" / "LHP-SUBSTANSI-MEMO.docx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    return {"content": [{"type": "text", "text": f"OK|format=memo|n_pertanyaan={len(items)}|{out_path.name}"}]}


_RB_DIM = [
    ("ketepatan", "Ketepatan Pelaksanaan"),
    ("ketercapaian", "Ketercapaian Output"),
    ("kualitas", "Kualitas Pelaksanaan"),
    ("kesesuaian", "Kesesuaian Waktu"),
]


def _render_rb(folder: Path, args: dict) -> dict:
    """Evaluasi RB: tabel komponen Renaksi × 4 dimensi (Sesuai/Tidak Sesuai)."""
    pen_path = folder / "_LHP" / "penilaian-rb.json"
    if not pen_path.exists():
        return {"content": [{"type": "text", "text": "FAILED|_LHP/penilaian-rb.json belum ada (pakai write_penilaian_rb)"}], "is_error": True}
    try:
        data = json.loads(pen_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {"content": [{"type": "text", "text": f"FAILED|baca penilaian-rb.json: {e}"}], "is_error": True}
    komponen = data.get("komponen") if isinstance(data, dict) else None
    if not isinstance(komponen, list) or not komponen:
        return {"content": [{"type": "text", "text": "FAILED|penilaian-rb.json: 'komponen' kosong"}], "is_error": True}

    ctx = _ctx_lines(folder)
    doc = Document()
    doc.add_heading("LAPORAN HASIL EVALUASI REFORMASI BIROKRASI", level=0)
    doc.add_paragraph(args.get("judul") or "Laporan Hasil Evaluasi Reformasi Birokrasi")
    meta = doc.add_paragraph()
    meta.add_run(f"Auditan: {args.get('auditi') or ctx.get('obyek', '-')}\n")
    meta.add_run(f"Dasar: {args.get('dasar_permintaan') or ctx.get('nomor st', '-')}\n")
    meta.add_run(f"Kode penugasan: {ctx.get('kode', folder.name)}")

    doc.add_heading("Penilaian per Komponen Rencana Aksi (4 Dimensi)", level=1)
    table = doc.add_table(rows=1, cols=2 + len(_RB_DIM))
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "Komponen Renaksi"
    for j, (_, label) in enumerate(_RB_DIM, start=1):
        hdr[j].text = label
    hdr[1 + len(_RB_DIM)].text = "Catatan"
    for k in komponen:
        row = table.add_row().cells
        row[0].text = str(k.get("nama", "-"))
        for j, (key, _) in enumerate(_RB_DIM, start=1):
            row[j].text = str(k.get(key, "-"))
        row[1 + len(_RB_DIM)].text = str(k.get("catatan", ""))

    if data.get("analisis_dampak"):
        doc.add_heading("Analisis Dampak", level=1)
        doc.add_paragraph(str(data["analisis_dampak"]))
    aoi = data.get("aoi") or []
    if isinstance(aoi, list) and aoi:
        doc.add_heading("Area of Improvement (AoI)", level=1)
        for a in aoi:
            doc.add_paragraph(str(a), style="List Bullet")

    out_path = folder / "_LHP" / "LHP-SUBSTANSI-RB.docx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    return {"content": [{"type": "text", "text": f"OK|format=rb-4dim|n_komponen={len(komponen)}|{out_path.name}"}]}


def _render_pendampingan(folder: Path, args: dict) -> dict:
    """Laporan Hasil Pendampingan (profil baru utk konsultasi-pengadaan).

    Beda dengan Memo: bukan jawab pertanyaan, melainkan LOG kegiatan
    pendampingan yang sudah diselesaikan. Sesuai pola Inspektorat II Komdigi
    yang sering pendampingan berkelanjutan (hadir rapat, reviu bertahap,
    klarifikasi proses) bukan konsultasi sekali jadi.

    Input: `_LHP/kegiatan-pendampingan.json` — list of:
        {tanggal, jenis_kegiatan, deskripsi, hasil,
         pihak_didampingi?, dokumen_pendukung?[], tindak_lanjut?}

    Output: `_LHP/LHP-PENDAMPINGAN.docx` — BAB I Kegiatan Pendampingan +
    BAB II Tindak Lanjut + Kesimpulan.
    """
    keg_path = folder / "_LHP" / "kegiatan-pendampingan.json"
    if not keg_path.exists():
        return {
            "content": [{
                "type": "text",
                "text": (
                    "FAILED|_LHP/kegiatan-pendampingan.json belum ada "
                    "(pakai append_kegiatan_pendampingan)"
                ),
            }],
            "is_error": True,
        }
    try:
        items = json.loads(keg_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return {
            "content": [{"type": "text", "text": f"FAILED|baca kegiatan: {e}"}],
            "is_error": True,
        }
    if not isinstance(items, list) or not items:
        return {
            "content": [{"type": "text", "text": "FAILED|kegiatan-pendampingan.json kosong"}],
            "is_error": True,
        }

    ctx = _ctx_lines(folder)
    doc = Document()
    doc.add_heading("LAPORAN HASIL PENDAMPINGAN PENGADAAN", level=0)
    doc.add_paragraph(args.get("judul") or "Laporan Hasil Pendampingan Pengadaan")

    meta = doc.add_paragraph()
    meta.add_run(f"Auditan: {args.get('auditi') or ctx.get('obyek', '-')}\n")
    meta.add_run(f"Dasar Penugasan: {args.get('dasar_permintaan') or ctx.get('nomor st', '-')}\n")
    meta.add_run(f"Kode penugasan: {ctx.get('kode', folder.name)}\n")
    # Periode pendampingan: tanggal min-max dari kegiatan
    tgls = sorted([str(it.get("tanggal", "")) for it in items if it.get("tanggal")])
    if tgls:
        periode = f"{tgls[0]} s.d. {tgls[-1]}" if tgls[0] != tgls[-1] else tgls[0]
        meta.add_run(f"Periode Pendampingan: {periode}\n")

    p = doc.add_paragraph()
    p.add_run(
        "Catatan: Laporan ini berisi rangkaian KEGIATAN PENDAMPINGAN yang "
        "telah diselesaikan tim Inspektorat II atas permintaan unit kerja. "
        "Pendampingan bersifat advisory dan preventif — tidak memberikan "
        "keyakinan dan tidak mengikat pejabat berwenang."
    ).italic = True

    # Gambaran umum (opsional)
    if args.get("gambaran_umum"):
        doc.add_heading("Gambaran Umum", level=1)
        doc.add_paragraph(str(args["gambaran_umum"]))

    # BAB I — Kegiatan Pendampingan
    doc.add_heading(f"I. Kegiatan Pendampingan yang Telah Diselesaikan ({len(items)})", level=1)
    table = doc.add_table(rows=1, cols=6)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    headers = ["No", "Tanggal", "Jenis Kegiatan", "Pihak Didampingi", "Deskripsi", "Hasil"]
    for i, h in enumerate(headers):
        hdr[i].text = h
    for i, it in enumerate(items, start=1):
        row = table.add_row().cells
        row[0].text = str(i)
        row[1].text = str(it.get("tanggal", "-"))
        row[2].text = str(it.get("jenis_kegiatan", "-"))
        row[3].text = str(it.get("pihak_didampingi", "-"))
        row[4].text = str(it.get("deskripsi", "-"))
        row[5].text = str(it.get("hasil", "-"))

    # Dokumen pendukung (per kegiatan, kalau ada)
    has_dok = any(it.get("dokumen_pendukung") for it in items)
    if has_dok:
        doc.add_heading("Dokumen Pendukung per Kegiatan", level=2)
        for i, it in enumerate(items, start=1):
            doks = it.get("dokumen_pendukung") or []
            if not isinstance(doks, list) or not doks:
                continue
            doc.add_paragraph(f"Kegiatan #{i} ({it.get('tanggal', '-')})").bold = True
            for d in doks:
                doc.add_paragraph(str(d), style="List Bullet")

    # BAB II — Tindak Lanjut
    tindak_lanjut = [it for it in items if it.get("tindak_lanjut")]
    if tindak_lanjut:
        doc.add_heading(f"II. Hal yang Masih Memerlukan Tindak Lanjut ({len(tindak_lanjut)})", level=1)
        for i, it in enumerate(tindak_lanjut, start=1):
            p2 = doc.add_paragraph()
            p2.add_run(f"{i}. {it.get('jenis_kegiatan', '-')} ({it.get('tanggal', '-')}): ").bold = True
            p2.add_run(str(it.get("tindak_lanjut", "")))

    # Kesimpulan (template singkat — auditor bisa edit DOCX)
    doc.add_heading("III. Kesimpulan", level=1)
    doc.add_paragraph(
        args.get("kesimpulan")
        or (
            f"Tim Inspektorat II telah menyelesaikan {len(items)} kegiatan pendampingan "
            f"pengadaan pada {args.get('auditi') or ctx.get('obyek', 'unit kerja')}. "
            f"Seluruh kegiatan diarahkan untuk mencegah penyimpangan prosedur "
            f"pengadaan dan memberikan masukan teknis berbasis Perpres 16/2018 "
            f"jo. 12/2021. Pendampingan ini tidak menggantikan kewenangan "
            f"PPK/PA/KPA atas keputusan pengadaan."
        )
    )

    out_path = folder / "_LHP" / "LHP-PENDAMPINGAN.docx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out_path)
    return {
        "content": [{
            "type": "text",
            "text": (
                f"OK|format=pendampingan|n_kegiatan={len(items)}|"
                f"n_tindak_lanjut={len(tindak_lanjut)}|{out_path.name}"
            ),
        }]
    }


@tool(
    "append_kegiatan_pendampingan",
    "Tambah satu kegiatan pendampingan ke `_LHP/kegiatan-pendampingan.json` "
    "(skill konsultasi-pengadaan, profil 'pendampingan'). Schema: "
    "{tanggal: 'YYYY-MM-DD', jenis_kegiatan: 'Rapat|Reviu|Klarifikasi|Pendampingan langsung|...', "
    "deskripsi: 'apa yg auditor lakukan', hasil: 'apa yg berhasil diselesaikan', "
    "pihak_didampingi?: 'PPK/PA/Pokja Pemilihan/dst', "
    "dokumen_pendukung?: ['Notulen rapat tanggal X', 'Draft KAK rev-2', ...], "
    "tindak_lanjut?: 'hal yg masih perlu diselesaikan auditi'}. "
    "Konsultasi-pengadaan TIDAK pakai temuan KKSA dan TIDAK pakai memo — pakai "
    "log kegiatan ini, lalu render_report.",
    {"penugasan_folder": str, "kegiatan": dict},
)
async def append_kegiatan_pendampingan(args: dict) -> dict:
    path = Path(args["penugasan_folder"]) / "_LHP" / "kegiatan-pendampingan.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    items: list = []
    if path.exists():
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                items = []
        except (json.JSONDecodeError, OSError):
            items = []
    new = args.get("kegiatan")
    if isinstance(new, list):
        items.extend(new)
    elif isinstance(new, dict):
        items.append(new)
    else:
        return {
            "content": [{"type": "text", "text": "FAILED|param 'kegiatan' harus dict atau list of dict"}],
            "is_error": True,
        }
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return {
        "content": [{
            "type": "text",
            "text": f"OK|total_kegiatan={len(items)} @ {path}",
        }]
    }


@tool(
    "append_saran",
    "Tambah butir Memo Konsultansi ke _LHP/saran.json (untuk skill konsultansi). "
    "`saran` = dict/list of {pertanyaan, dasar_hukum[], pendapat, saran}. Konsultansi "
    "tidak memakai temuan KKSA — pakai ini lalu render_report.",
    {"penugasan_folder": str, "saran": dict},
)
async def append_saran(args: dict) -> dict:
    path = Path(args["penugasan_folder"]) / "_LHP" / "saran.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    items = []
    if path.exists():
        try:
            items = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(items, list):
                items = []
        except (json.JSONDecodeError, OSError):
            items = []
    new = args.get("saran")
    items.extend(new if isinstance(new, list) else [new])
    path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"content": [{"type": "text", "text": f"OK|total_saran={len(items)}"}]}


@tool(
    "write_penilaian_rb",
    "Tulis (overwrite) _LHP/penilaian-rb.json untuk Evaluasi RB. Struktur: "
    "{komponen:[{nama, ketepatan, ketercapaian, kualitas, kesesuaian, catatan}], "
    "analisis_dampak, aoi:[...]}. Nilai dimensi 'Sesuai'/'Tidak Sesuai'. Sumber: hasil "
    "gate evaluasi RB. Lalu render_report.",
    {"penugasan_folder": str, "penilaian": dict},
)
async def write_penilaian_rb(args: dict) -> dict:
    path = Path(args["penugasan_folder"]) / "_LHP" / "penilaian-rb.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(args["penilaian"], ensure_ascii=False, indent=2), encoding="utf-8")
    n = len((args["penilaian"] or {}).get("komponen", []))
    return {"content": [{"type": "text", "text": f"OK|n_komponen={n}"}]}


def _latest_lhp_docx(folder: Path) -> Path | None:
    """Docx laporan hasil terbaru di _LHP/ (hasil render_report) untuk disisipi
    tabel/diagram. Abaikan file lock Word (~$)."""
    lhp = folder / "_LHP"
    if not lhp.is_dir():
        return None
    docs = [p for p in lhp.glob("*.docx") if not p.name.startswith("~$")]
    return max(docs, key=lambda p: p.stat().st_mtime) if docs else None


@tool(
    "append_lampiran_tabel",
    "Sisipkan TABEL ke laporan hasil (docx terbaru di _LHP/) — mis. rekap temuan per "
    "aspek, matriks nilai/severity, status tindak lanjut. Data WAJIB dari sumber "
    "kebenaran (temuan.json/TLHP/konteks), JANGAN dikarang. Panggil SETELAH render_report. "
    "Args: judul (caption), headers (list kolom), rows (list of list, per baris).",
    {"penugasan_folder": str, "judul": str, "headers": list, "rows": list},
)
async def append_lampiran_tabel(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    doc_path = _latest_lhp_docx(folder)
    if doc_path is None:
        return {"content": [{"type": "text", "text": "FAILED|laporan di _LHP belum ada — render_report dulu"}], "is_error": True}
    headers = args.get("headers") or []
    rows = args.get("rows") or []
    if not headers or not rows:
        return {"content": [{"type": "text", "text": "FAILED|headers & rows wajib (list non-kosong)"}], "is_error": True}
    try:
        doc = Document(str(doc_path))
        doc.add_heading(str(args.get("judul") or "Tabel"), level=2)
        table = doc.add_table(rows=1, cols=len(headers))
        try:
            table.style = "Light Grid Accent 1"
        except Exception:  # noqa: BLE001 — style opsional
            pass
        for i, h in enumerate(headers):
            table.rows[0].cells[i].text = str(h)
        for r in rows:
            cells = table.add_row().cells
            for i in range(len(headers)):
                cells[i].text = str(r[i]) if isinstance(r, (list, tuple)) and i < len(r) else ""
        doc.save(str(doc_path))
    except Exception as e:  # noqa: BLE001
        return {"content": [{"type": "text", "text": f"FAILED|tulis tabel: {e}"}], "is_error": True}
    return {"content": [{"type": "text", "text": f"OK|tabel '{args.get('judul')}' ({len(rows)} baris) → {doc_path.name}"}]}


@tool(
    "append_lampiran_diagram",
    "Sisipkan DIAGRAM gambar (bar/pie/line) ke laporan hasil (docx terbaru di _LHP/) — "
    "mis. jumlah temuan per severity/aspek, status TL. Data WAJIB dari sumber kebenaran, "
    "JANGAN dikarang. Panggil SETELAH render_report. Args: judul, tipe ('bar'|'pie'|'line'), "
    "kategori (list label), nilai (list angka, sama panjang dgn kategori).",
    {"penugasan_folder": str, "judul": str, "tipe": str, "kategori": list, "nilai": list},
)
async def append_lampiran_diagram(args: dict) -> dict:
    folder = Path(args["penugasan_folder"])
    doc_path = _latest_lhp_docx(folder)
    if doc_path is None:
        return {"content": [{"type": "text", "text": "FAILED|laporan di _LHP belum ada — render_report dulu"}], "is_error": True}
    kategori = args.get("kategori") or []
    nilai = args.get("nilai") or []
    if not kategori or len(kategori) != len(nilai):
        return {"content": [{"type": "text", "text": "FAILED|kategori & nilai wajib & sama panjang"}], "is_error": True}
    try:
        nums = [float(x) for x in nilai]
    except (TypeError, ValueError):
        return {"content": [{"type": "text", "text": "FAILED|nilai harus angka"}], "is_error": True}
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return {"content": [{"type": "text", "text": "FAILED|matplotlib belum terpasang — pakai append_lampiran_tabel sebagai gantinya"}], "is_error": True}
    tipe = (args.get("tipe") or "bar").lower()
    judul = str(args.get("judul") or "Diagram")
    labels = [str(k) for k in kategori]
    try:
        fig, ax = plt.subplots(figsize=(6.2, 3.6))
        if tipe == "pie":
            ax.pie(nums, labels=labels, autopct="%1.0f%%", startangle=90)
            ax.axis("equal")
        elif tipe == "line":
            ax.plot(labels, nums, marker="o", color="#0f766e")
            ax.grid(True, axis="y", alpha=0.3)
        else:  # bar (default)
            ax.bar(labels, nums, color="#1d4a73")
            ax.grid(True, axis="y", alpha=0.3)
        ax.set_title(judul)
        if tipe != "pie":
            fig.autofmt_xdate(rotation=20)
        fig.tight_layout()
        slug = re.sub(r"[^a-z0-9]+", "-", judul.lower()).strip("-")[:32] or "diagram"
        img = folder / "_LHP" / f"_diagram-{slug}.png"
        fig.savefig(str(img), dpi=130)
        plt.close(fig)
        from docx.shared import Inches
        doc = Document(str(doc_path))
        doc.add_heading(judul, level=2)
        doc.add_picture(str(img), width=Inches(5.5))
        doc.save(str(doc_path))
    except Exception as e:  # noqa: BLE001
        return {"content": [{"type": "text", "text": f"FAILED|buat diagram: {e}"}], "is_error": True}
    return {"content": [{"type": "text", "text": f"OK|diagram {tipe} '{judul}' → {doc_path.name}"}]}


@tool(
    "render_daftar_temuan",
    "Hasilkan/perbarui 'Daftar Temuan & Rekomendasi' (DHP) di _LHP/ dari temuan.json + "
    "rekomendasi.json — paket EKSPOR ke administrasi/TU (kolom Tindak Lanjut/PIC/Target "
    "dikosongkan untuk diisi TU). Otomatis juga dibuat saat LHP disetujui; tool ini untuk regen manual.",
    {"penugasan_folder": str},
)
async def render_daftar_temuan(args: dict) -> dict:
    from app.export_dhp import build_daftar_temuan_rekomendasi
    p = build_daftar_temuan_rekomendasi(Path(args["penugasan_folder"]))
    if p is None:
        return {"content": [{"type": "text", "text": "FAILED|tak ada temuan (temuan.json kosong/absen)"}], "is_error": True}
    return {"content": [{"type": "text", "text": f"OK|Daftar Temuan & Rekomendasi → {p.name}"}]}


LHR_TOOLS = [
    write_sasaran_assignment,  # Setup Penugasan mode
    read_temuan_json,
    check_completeness,
    write_rekomendasi_json,
    render_report,     # dispatcher per-profil (kksa/memo/rb-4dim/pendampingan) — jalur utama LHP
    # Jalur BARU khusus reviu-pengadaan (13 Agu 2026) — berdampingan, bukan pengganti.
    write_narasi_laporan,
    render_lhr_narasi,
    append_saran,      # Memo Konsultansi (konsultansi-umum)
    append_kegiatan_pendampingan,  # Laporan Pendampingan (konsultasi-pengadaan)
    write_penilaian_rb,  # Evaluasi RB 4-dimensi
    append_lampiran_tabel,    # 1B — tabel rekap ke laporan (data dari sumber kebenaran)
    append_lampiran_diagram,  # 1B — diagram bar/pie/line ke laporan (matplotlib)
    render_daftar_temuan,     # 3 — Daftar Temuan & Rekomendasi (ekspor ke administrasi/TU)
    run_qc_lhp,
]

"""Routes manajemen penugasan."""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

from fastapi import APIRouter, BackgroundTasks, Body, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Dokumen, DokumenStatus, LhpReview, Penugasan, PenugasanStatus, Role, TemuanReview, User
from app.tenancy import assert_akses_penugasan, filter_penugasan, inspektorat_user
from app.schemas import PenugasanCreate, PenugasanOut
from app.storage import (
    INPUT_JENIS,
    append_audit_trail,
    compute_penugasan_status,
    context_readiness,
    delete_penugasan_folder,
    gen_kode_penugasan,
    penugasan_folder,
)

router = APIRouter(prefix="/penugasan", tags=["penugasan"])


def _scaffold_penugasan_files(folder: Path, kode: str, payload: PenugasanCreate, ketua_tim_name: str | None) -> None:
    """Tulis stub context.md + sasaran-assignment.json saat penugasan dibuat.

    V6 (qc_saipi.py, render_kkp.py) butuh kedua file ini ada di lokasi standar:
    - {folder}/context.md
    - {folder}/_PKP/sasaran-assignment.json

    Format mengikuti yang dibaca parse_context_meta() di V6.
    """
    # 1. context.md stub (placeholder fields yang nanti diisi Ketua Tim)
    context_md_path = folder / "context.md"
    if not context_md_path.exists():
        skill_label = payload.skill.replace("-", " ").title()
        # tanggal_st bertipe str (schema) — namun data lama bisa berupa date.
        _t = payload.tanggal_st
        tanggal_str = (
            _t.strftime("%d %B %Y") if hasattr(_t, "strftime") else (str(_t) if _t else "[DIISI AUDITOR]")
        )
        content = f"""# Konteks Penugasan: {payload.obyek}

## Identitas Penugasan

- Kode: {kode}
- Obyek: {payload.obyek}
- Skill / Jenis Pengawasan: {payload.skill}
- Nomor ST: {payload.nomor_st or "[DIISI AUDITOR]"}
- Tanggal ST: {tanggal_str}

## Periode & Anggaran

- Periode: [DIISI AUDITOR — mis. Januari–Desember 2026]
- Tahun Anggaran: [DIISI AUDITOR — mis. 2026]

## Tujuan

[DIISI AUDITOR — sebutkan tujuan reviu sesuai PKP. Contoh:
"Memberikan keyakinan terbatas atas kewajaran HPS dan kepatuhan proses
pengadaan terhadap Perpres 16/2018 jo. Perpres 12/2021."]

## Ruang Lingkup

[DIISI AUDITOR — batas objek, periode, dan tahapan yang dicakup. Contoh:
"Paket Pengadaan Perangkat Jaringan TA 2025, tahap perencanaan sampai
penetapan HPS."]

## Tim

| Peran | Nama Lengkap | NIP | Jabfung |
|-------|--------------|-----|---------|
| Ketua Tim | {ketua_tim_name or "[DIISI]"} | [NIP] | [Auditor Madya/Muda/Pertama] |
| Anggota | [DIISI] | [NIP] | [Auditor Pertama] |

## Ringkasan Obyek

[DIISI — 3-5 kalimat gambaran umum obyek yang direviu: nilai pengadaan,
periode pelaksanaan, instansi auditi, dll.]
"""
        context_md_path.write_text(content, encoding="utf-8")

    # 2. _PKP/sasaran-assignment.json stub (kosong, auditor lengkapi)
    sasaran_path = folder / "_PKP" / "sasaran-assignment.json"
    if not sasaran_path.exists():
        sasaran_path.parent.mkdir(parents=True, exist_ok=True)
        stub = {
            "penugasan_id": kode,
            "skill": payload.skill,
            "schema_version": "v4.0.0",
            "tanggal_dibuat": datetime.utcnow().isoformat() + "Z",
            "sasaran": [
                # Contoh struktur — dihapus/diganti oleh Ketua Tim:
                # {
                #     "sasaran_id": "S-01",
                #     "deskripsi": "Kewajaran HPS",
                #     "assigned_to": ["Nama Anggota Tim"],
                #     "langkah_kerja": ["..."]
                # }
            ],
        }
        sasaran_path.write_text(json.dumps(stub, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3. temuan.json stub di _KKP/ supaya render_kkp.py tidak crash bila auditor
    #    coba render sebelum ada temuan. Skema mengikuti render_kkp.py.
    temuan_path = folder / "_KKP" / "temuan.json"
    if not temuan_path.exists():
        temuan_path.parent.mkdir(parents=True, exist_ok=True)
        stub_temuan = {
            "penugasan": {
                "kode": kode,
                "obyek": payload.obyek,
                "jenis_pengawasan": payload.skill,
                "nomor_st": payload.nomor_st or "[DIISI AUDITOR]",
                "tanggal_st": (payload.tanggal_st.isoformat() if hasattr(payload.tanggal_st, "isoformat") else payload.tanggal_st) if payload.tanggal_st else None,
            },
            "schema_version": "v4.0.0",
            "temuan": [],
        }
        temuan_path.write_text(json.dumps(stub_temuan, ensure_ascii=False, indent=2), encoding="utf-8")


async def _dokumen_status_map(db: AsyncSession, penugasan_ids: list[int]) -> dict[int, list[str]]:
    """Status semua dokumen di-group per penugasan_id (untuk derive status)."""
    out: dict[int, list[str]] = {}
    if not penugasan_ids:
        return out
    rows = (
        await db.execute(
            select(Dokumen.penugasan_id, Dokumen.status).where(
                Dokumen.penugasan_id.in_(penugasan_ids)
            )
        )
    ).all()
    for pid, st in rows:
        out.setdefault(pid, []).append(st if isinstance(st, str) else st.value)
    return out


def _load_temuan_json(folder: Path) -> list[dict]:
    """Baca `_KKP/temuan.json` → list temuan dict. Return [] kalau tidak ada."""
    p = folder / "_KKP" / "temuan.json"
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    out = data.get("temuan") if isinstance(data, dict) else []
    return out if isinstance(out, list) else []


def _with_derived_status(p: Penugasan, dok_statuses: list[str]) -> PenugasanOut:
    out = PenugasanOut.model_validate(p)
    out.status = compute_penugasan_status(Path(p.folder_path), dok_statuses, stored_status=p.status)
    return out



# ── Saran sasaran dari penugasan historis ────────────────────────────────────
# Di-port dari `knowledge_browse` (modul itu dicabut di turunan FREE karena
# bergantung wiki). Fungsi ini murni: hanya membaca sasaran-assignment.json
# milik penugasan lain DI INSPEKTORAT YANG SAMA (penyaringan dilakukan pemanggil).
_WORD_RE = re.compile(r"[a-z0-9]+")
_ID_STOPWORDS = {
    "dan", "atau", "atas", "di", "ke", "dari", "untuk", "yang", "dengan",
    "pada", "oleh", "dalam", "ini", "itu", "akan", "telah", "sudah",
    "ta", "tahun", "anggaran", "periode", "tahap", "fase",
    "kementerian", "kemkomdigi", "komdigi", "kominfo",
    "ditjen", "direktorat", "dit", "sub", "satker", "satuan", "kerja", "unit",
    "the", "of", "a",
}


def _tokenize(text: str) -> set[str]:
    if not text:
        return set()
    return {t for t in _WORD_RE.findall(text.lower())
            if len(t) >= 3 and t not in _ID_STOPWORDS}


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    union = len(a | b)
    return len(a & b) / union if union else 0.0


def _saran_historis(candidates: list[dict], skill: str, obyek: str, top_n: int = 5) -> list[dict]:
    """Penugasan historis ber-skill sama, di-rank kemiripan obyek (Jaccard)."""
    target = _tokenize(obyek)
    out: list[dict] = []
    for c in candidates:
        if c.get("skill") != skill or not c.get("folder_path"):
            continue
        sa_path = Path(c["folder_path"]) / "_PKP" / "sasaran-assignment.json"
        if not sa_path.exists():
            continue
        try:
            sasaran = (json.loads(sa_path.read_text(encoding="utf-8")) or {}).get("sasaran") or []
        except (json.JSONDecodeError, OSError):
            continue
        if not sasaran:
            continue
        out.append({
            "kode": c.get("kode"), "obyek": c.get("obyek"), "skill": c.get("skill"),
            "status": c.get("status"),
            "similarity": round(_jaccard(target, _tokenize(c.get("obyek", ""))), 3),
            "total_sasaran": len(sasaran),
            "sasaran": [{
                "sasaran_id": str(s.get("sasaran_id") or s.get("id") or "").strip(),
                "deskripsi": str(s.get("deskripsi") or s.get("nama") or "").strip(),
                "assigned_to": s.get("assigned_to") if isinstance(s.get("assigned_to"), list) else [],
                "langkah_kerja": s.get("langkah_kerja") if isinstance(s.get("langkah_kerja"), list) else [],
            } for s in sasaran],
        })
    out.sort(key=lambda x: x["similarity"], reverse=True)
    return out[:top_n]

@router.post("", response_model=PenugasanOut, status_code=status.HTTP_201_CREATED)
async def create_penugasan(
    payload: PenugasanCreate,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PenugasanOut:
    """Hanya Pengendali Teknis (PT) yang boleh buat penugasan baru.

    Workflow: PT create → KT setup → AT upload+analisis → KT approve + LHR.

    Turunan FREE: TANPA auto-build `_PRELOAD/context-bundle.md` — modul
    `preload_context` bergantung wiki dan sudah dicabut. Konteks pattern/
    regulasi dibaca agen langsung dari referensi skill (snapshot injeksi).
    """
    user, role = current
    if role != Role.PT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Hanya Pengendali Teknis (PT) yang boleh buat penugasan baru. Role Anda: {role.value}.",
        )

    kode = gen_kode_penugasan(payload.skill)
    folder = penugasan_folder(kode)

    # Scaffolding file V6 — context.md template, sasaran-assignment.json kosong,
    # temuan.json envelope. ketua_tim_name dikosongkan (di-assign saat KT setup).
    _scaffold_penugasan_files(
        folder=folder,
        kode=kode,
        payload=payload,
        ketua_tim_name=None,
    )

    p = Penugasan(
        kode=kode,
        obyek=payload.obyek,
        skill=payload.skill,
        jenis_penugasan=payload.jenis_penugasan,
        sub_penugasan=payload.sub_penugasan,
        nomor_st=payload.nomor_st,
        tanggal_st=payload.tanggal_st,
        status=PenugasanStatus.DRAFT,
        # ISOLASI: penugasan mewarisi Inspektorat pembuatnya (PT) — penentu
        # siapa saja yang nanti boleh melihat/mengolahnya.
        inspektorat=inspektorat_user(user),
        ketua_tim_id=None,  # ditetapkan saat KT setup
        folder_path=str(folder),
    )
    db.add(p)
    await db.flush()
    await db.refresh(p)

    return PenugasanOut.model_validate(p)


@router.get("", response_model=list[PenugasanOut])
async def list_penugasan(
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[PenugasanOut]:
    # ISOLASI: hanya penugasan milik Inspektorat pengguna (disaring di SQL).
    stmt = filter_penugasan(select(Penugasan), current[0]).order_by(Penugasan.created_at.desc())
    rows = (await db.execute(stmt)).scalars().all()
    dok_map = await _dokumen_status_map(db, [r.id for r in rows])
    return [_with_derived_status(r, dok_map.get(r.id, [])) for r in rows]


@router.get("/deteksi-skill")
async def deteksi_skill_dari_judul(
    judul: str = "",
    _current: tuple[User, Role] = Depends(get_current_user),
) -> dict[str, Any]:
    """Tebak Jenis & Sub dari judul penugasan + skill yang dihasilkannya.

    Hanya PEMBANTU PENGISIAN: hasilnya menjadi isian awal yang tinggal
    dibenarkan Pengendali Teknis. Yang mengikat tetap Jenis + Sub yang dipilih,
    bukan tebakan ini — judul bisa memuat dua kata kunci sekaligus, dan menebak
    dalam keadaan begitu berarti mengunci penugasan ke skill yang keliru.
    """
    from app.deteksi_skill import deteksi

    return deteksi(judul)


@router.get("/{penugasan_id}", response_model=PenugasanOut)
async def get_penugasan(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PenugasanOut:
    p = (
        await db.execute(select(Penugasan).where(Penugasan.id == penugasan_id))
    ).scalar_one_or_none()
    assert_akses_penugasan(p, current[0])  # ISOLASI: milik Inspektorat lain → 404
    dok_map = await _dokumen_status_map(db, [p.id])
    return _with_derived_status(p, dok_map.get(p.id, []))


@router.delete("/{penugasan_id}", status_code=status.HTTP_200_OK)
async def delete_penugasan(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Hapus penugasan beserta seluruh file di disk (hard delete). Hanya PT.

    Cascade ORM menghapus dokumen + agent_runs terkait. Folder penugasan di
    disk dihapus permanen.
    """
    user, role = current
    if role != Role.PT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Hanya Pengendali Teknis (PT) yang boleh hapus penugasan. Role Anda: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    kode = p.kode

    await db.delete(p)
    await db.commit()
    delete_penugasan_folder(folder)

    return {"ok": True, "deleted": kode, "folder_removed": str(folder)}


# ============================================================
# SETUP PENUGASAN — endpoint untuk Ketua Tim mengelola sasaran-assignment + context
# Hanya role KT/PT/PM yang bisa PUT. Role apapun bisa GET.
# ============================================================


class SasaranItem(BaseModel):
    """Schema 1 sasaran untuk sasaran-assignment.json.

    Sesuai yang dibaca V6 qc_saipi.py: butuh sasaran_id, assigned_to, dan
    optional langkah_kerja. status default AKTIF, diubah ke SELESAI_KKP
    oleh AT setelah temuan ter-input.
    """

    sasaran_id: str = Field(..., min_length=1, description="ID unik, mis. S-PBJ-01")
    deskripsi: str = Field(default="", description="Deskripsi sasaran")
    assigned_to: list[str] = Field(default_factory=list, description="Nama anggota tim")
    langkah_kerja: list[str] = Field(default_factory=list)
    status: str = Field(default="AKTIF")
    # Kolom PKP format INTEGRAL/SIMWAS: Sasaran | Langkah Kerja | Dilaksanakan
    # Oleh | Waktu | No KKP. Dua kolom terakhir disimpan di sini.
    waktu: str | None = Field(default=None, description="Periode pelaksanaan (kolom Waktu PKP SIMWAS)")
    no_kkp: str | None = Field(default=None, description="Nomor KKP (kolom No KKP PKP SIMWAS)")
    # Cara KKSA sasaran ini disusun. Disimpan PER SASARAN, bukan per penugasan:
    # satu penugasan realistis campur — sasaran A cukup dikerjakan manual,
    # sasaran B minta bantuan agen. Mengunci di tingkat penugasan memaksa
    # auditor memilih terlalu dini.
    #   AI      : agen menganalisis dokumen objek lalu menyusun KKSA (skema 1)
    #   CATATAN : agen merumuskan KKSA dari catatan/analisis awal auditor (skema 2)
    #   MANUAL  : auditor menulis KKSA sendiri, tanpa agen (skema 3)
    #
    # PEMILIK FIELD INI = ANGGOTA TIM, bukan Ketua Tim. Cara penyusunan adalah
    # keputusan pelaksana saat menyusun kertas kerja (Tahapan 3) — bukan bagian
    # dari perencanaan PKP (Tahapan 2). KT merencanakan APA yang direviu
    # (sasaran + langkah kerja + siapa); AT memilih BAGAIMANA kertas kerjanya
    # disusun setelah melihat dokumen yang ada di tangannya. Diubah lewat
    # PUT /penugasan/{id}/sasaran/{sasaran_id}/mode (lihat di bawah); PUT
    # sasaran-assignment milik KT sengaja TIDAK menimpanya.
    mode: Literal["AI", "CATATAN", "MANUAL"] = Field(default="AI")


class LangkahUmum(BaseModel):
    """Langkah kerja umum PKP format INTEGRAL (kelompok I. Perencanaan /
    III. Pelaporan) — tiap langkah punya Pelaksana + Waktu."""

    langkah: str = Field(default="")
    pelaksana: str = Field(default="")
    waktu: str = Field(default="")


class SasaranAssignmentPayload(BaseModel):
    sasaran: list[SasaranItem]
    # Meta PKP format INTEGRAL (hasil bedah form live simwasv2 10 Jun 2026):
    # nomor PKP + langkah kelompok I (Perencanaan) & III (Pelaporan).
    # Kelompok II (Pelaksanaan) = `sasaran` di atas (dari Kartu Penugasan).
    nomor_pkp: str | None = None
    langkah_perencanaan: list[LangkahUmum] | None = None
    langkah_pelaporan: list[LangkahUmum] | None = None


def _require_sasaran_setup_role(role: Role) -> None:
    """Hanya KT yang boleh edit sasaran-assignment. PT bisa juga (override)."""
    if role not in (Role.KT, Role.PT):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Role {role.value} tidak boleh edit sasaran-assignment. Hanya KT/PT.",
        )


def _require_context_edit_role(role: Role) -> None:
    """KT setup awal context.md, AT penyempurnaan saat analisis."""
    if role not in (Role.KT, Role.PT, Role.AT):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Role {role.value} tidak boleh edit context.md.",
        )


async def _get_penugasan_or_404(
    db: AsyncSession, penugasan_id: int, current: tuple[User, Role]
) -> Penugasan:
    """Ambil penugasan + TEGAKKAN isolasi Inspektorat.

    `current` WAJIB (bukan opsional) supaya call-site yang lupa meneruskannya
    gagal keras saat dipanggil — bukan diam-diam melewati pemeriksaan akses.
    Penugasan milik Inspektorat lain dijawab 404 (lihat app/tenancy.py).
    """
    p = (
        await db.execute(select(Penugasan).where(Penugasan.id == penugasan_id))
    ).scalar_one_or_none()
    if not p:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Penugasan tidak ditemukan")
    return assert_akses_penugasan(p, current[0])


class UbahSkillPayload(BaseModel):
    jenis_penugasan: str | None = None
    sub_penugasan: str | None = None
    skill: str | None = None
    alasan: str | None = None


# Tahap yang masih boleh diubah skill-nya. Setelah kertas kerja mulai disusun,
# mengganti skill akan membuat temuan yang sudah ada tidak selaras dengan
# pipeline, format laporan, dan doktrin agennya — jadi dikunci.
_STATUS_BOLEH_UBAH_SKILL = {
    PenugasanStatus.DRAFT,
    PenugasanStatus.KP_DONE,
    PenugasanStatus.PKP_KT_DONE,
    PenugasanStatus.PKP_DONE,
}


@router.put("/{penugasan_id}/skill")
async def ubah_skill(
    penugasan_id: int,
    payload: UbahSkillPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Koreksi Jenis/Sub (dan karenanya skill). Hanya PT, sebelum tahap KKP.

    Skill menentukan pipeline, format laporan, dan doktrin agen. Menggantinya di
    tengah jalan membuat temuan yang sudah tersusun tidak selaras — karena itu
    dibatasi ke tahap perencanaan, dan setiap koreksi dicatat siapa & kapan.
    """
    from app.deteksi_skill import jelaskan, skill_dari
    from app.skills_registry import available_slugs, skill_exists

    user, role = current
    if role != Role.PT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Hanya Pengendali Teknis (PT) yang boleh mengoreksi skill. Role Anda: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    st = p.status if isinstance(p.status, PenugasanStatus) else PenugasanStatus(p.status)
    if st not in _STATUS_BOLEH_UBAH_SKILL:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            f"Penugasan sudah masuk tahap {st.value} — skill tidak bisa diubah lagi karena "
            "kertas kerja sudah disusun berdasarkan skill yang sekarang. Bila memang keliru, "
            "buat penugasan baru.",
        )

    skill_baru = (payload.skill or "").strip().lower() or skill_dari(
        payload.jenis_penugasan, payload.sub_penugasan
    )
    if not skill_baru:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Jenis dan Sub Penugasan belum lengkap, dan skill tidak disebut eksplisit.",
        )
    if not skill_exists(skill_baru):
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            f"Skill '{skill_baru}' tidak terdaftar. Tersedia: {', '.join(available_slugs())}.",
        )

    lama = p.skill
    jejak = json.loads(p.skill_override) if p.skill_override else []
    if not isinstance(jejak, list):
        jejak = []
    jejak.append({
        "pada": datetime.utcnow().isoformat() + "Z",
        "oleh": user.nama_lengkap,
        "dari": lama,
        "ke": skill_baru,
        "jenis": payload.jenis_penugasan,
        "sub": payload.sub_penugasan,
        "alasan": (payload.alasan or "").strip(),
    })
    p.skill = skill_baru
    if payload.jenis_penugasan:
        p.jenis_penugasan = payload.jenis_penugasan
    if payload.sub_penugasan:
        p.sub_penugasan = payload.sub_penugasan
    p.skill_override = json.dumps(jejak, ensure_ascii=False)
    await db.flush()

    append_audit_trail(Path(p.folder_path), {
        "event": "skill_dikoreksi",
        "oleh": user.nama_lengkap,
        "dari": lama,
        "ke": skill_baru,
        "alasan": (payload.alasan or "").strip(),
    })
    return {
        "ok": True,
        "skill": skill_baru,
        "skill_sebelumnya": lama,
        "penjelasan": jelaskan(p.jenis_penugasan, p.sub_penugasan),
        "riwayat": jejak,
    }


@router.get("/{penugasan_id}/sasaran-assignment")
async def get_sasaran_assignment(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Read isi _PKP/sasaran-assignment.json — bisa diakses semua role.

    Auto-enrich status: kalau ada minimal 1 temuan untuk sasaran tertentu
    di _KKP/temuan.json, dan status masih AKTIF, otomatis upgrade ke
    SELESAI_KKP (KT lalu manual ubah ke DISETUJUI_KT setelah review).
    """
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    sa_path = folder / "_PKP" / "sasaran-assignment.json"

    if not sa_path.exists():
        return {
            "penugasan_id": p.kode,
            "skill": p.skill if isinstance(p.skill, str) else p.skill.value,
            "schema_version": "v4.0.0",
            "sasaran": [],
        }
    try:
        data = json.loads(sa_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "sasaran-assignment.json corrupt — perlu di-perbaiki manual",
        )

    # Auto-detect SELESAI_KKP berdasarkan temuan.json
    temuan_path = folder / "_KKP" / "temuan.json"
    sasaran_with_temuan: set[str] = set()
    if temuan_path.exists():
        try:
            temuan_data = json.loads(temuan_path.read_text(encoding="utf-8"))
            for t in temuan_data.get("temuan", []):
                sid = t.get("sasaran_id")
                if sid:
                    sasaran_with_temuan.add(sid)
        except json.JSONDecodeError:
            pass

    for s in data.get("sasaran", []):
        # Upgrade AKTIF → SELESAI_KKP kalau ada temuan, tapi jangan downgrade DISETUJUI_KT/DITOLAK_KT
        if s.get("status") == "AKTIF" and s.get("sasaran_id") in sasaran_with_temuan:
            s["status"] = "SELESAI_KKP"

    return data


@router.put("/{penugasan_id}/sasaran-assignment")
async def put_sasaran_assignment(
    penugasan_id: int,
    payload: SasaranAssignmentPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Overwrite _PKP/sasaran-assignment.json — hanya KT/PT."""
    user, role = current
    _require_sasaran_setup_role(role)
    p = await _get_penugasan_or_404(db, penugasan_id, current)

    # Validasi: sasaran_id unique
    ids = [s.sasaran_id for s in payload.sasaran]
    if len(ids) != len(set(ids)):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"sasaran_id duplikat ditemukan: {ids}",
        )

    folder = Path(p.folder_path)
    path = folder / "_PKP" / "sasaran-assignment.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    # `mode` (cara penyusunan KKSA) milik Anggota Tim, bukan KT — form PKP tidak
    # lagi menampilkannya. Simpan ulang nilai yang sudah ada di disk supaya
    # penyimpanan PKP oleh KT tidak diam-diam mengembalikan pilihan AT ke "AI".
    # Sasaran baru (belum ada di disk) memakai nilai dari payload/default.
    existing_mode: dict[str, str] = {}
    if path.exists():
        try:
            _prev = json.loads(path.read_text(encoding="utf-8"))
            for _s in _prev.get("sasaran", []):
                _sid, _m = _s.get("sasaran_id"), _s.get("mode")
                if _sid and _m in ("AI", "CATATAN", "MANUAL"):
                    existing_mode[str(_sid)] = _m
        except (json.JSONDecodeError, OSError):
            pass  # file rusak/tak terbaca → jatuh ke nilai payload

    sasaran_rows: list[dict[str, Any]] = []
    for s in payload.sasaran:
        row = s.model_dump()
        row["mode"] = existing_mode.get(s.sasaran_id, row.get("mode", "AI"))
        sasaran_rows.append(row)

    data = {
        "penugasan_id": p.kode,
        "skill": p.skill if isinstance(p.skill, str) else p.skill.value,
        "schema_version": "v4.0.0",
        "tanggal_dibuat": datetime.utcnow().isoformat() + "Z",
        "sasaran": sasaran_rows,
        # Meta PKP INTEGRAL — top-level keys tambahan; aman untuk V6 yang
        # hanya membaca key `sasaran`.
        "nomor_pkp": payload.nomor_pkp or "",
        "langkah_perencanaan": [l.model_dump() for l in (payload.langkah_perencanaan or [])],
        "langkah_pelaporan": [l.model_dump() for l in (payload.langkah_pelaporan or [])],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # v10.1 (transplant tahapan v8): KT simpan PKP → sentinel PKP_KT_DONE
    # (menunggu persetujuan PT via PUT /pkp/approve). Pastikan kp-saved.flag ada (compat).
    (folder / "_PKP" / "pkp-kt-saved.flag").write_text("saved", encoding="utf-8")
    _kp_flag = folder / "_PKP" / "kp-saved.flag"
    if not _kp_flag.exists():
        _kp_flag.write_text("saved", encoding="utf-8")

    # Render dokumen PKP ke 00-input/ → QC SAIPI REN-002 ("PKP tersedia di
    # 00-input/") terpenuhi. Format mengikuti PKP INTEGRAL (I. Perencanaan /
    # II. Pelaksanaan = sasaran / III. Pelaporan).
    def _langkah_md(rows: list) -> str:
        if not rows:
            return "_(belum diisi)_\n"
        out = "| Langkah Kerja | Pelaksana | Waktu |\n|---|---|---|\n"
        for r in rows:
            out += f"| {r.langkah} | {r.pelaksana} | {r.waktu} |\n"
        return out

    pkp_md = f"# PROGRAM KERJA PENGAWASAN\n\n**Nomor PKP**: {payload.nomor_pkp or '[DIISI]'}\n\n"
    pkp_md += "## I. Perencanaan\n\n" + _langkah_md(payload.langkah_perencanaan or []) + "\n"
    pkp_md += "## II. Pelaksanaan — Sasaran Pengawasan\n\n"
    pkp_md += "| Sasaran | Langkah Kerja | Dilaksanakan Oleh | Waktu | No KKP |\n|---|---|---|---|---|\n"
    for s in payload.sasaran:
        lk = "; ".join(s.langkah_kerja) if s.langkah_kerja else ""
        who = ", ".join(s.assigned_to) if s.assigned_to else ""
        pkp_md += f"| {s.deskripsi} | {lk} | {who} | {s.waktu or ''} | {s.no_kkp or ''} |\n"
    pkp_md += "\n## III. Pelaporan\n\n" + _langkah_md(payload.langkah_pelaporan or [])
    pkp_doc = folder / "00-input" / f"PKP-{p.kode}.md"
    pkp_doc.parent.mkdir(parents=True, exist_ok=True)
    pkp_doc.write_text(pkp_md, encoding="utf-8")

    return {
        "ok": True,
        "total_sasaran": len(payload.sasaran),
        "path": str(path.relative_to(folder)),
    }


class SasaranModePayload(BaseModel):
    """Cara penyusunan KKSA untuk 1 sasaran — dipilih Anggota Tim."""

    mode: Literal["AI", "CATATAN", "MANUAL"]


@router.put("/{penugasan_id}/sasaran/{sasaran_id}/mode")
async def put_sasaran_mode(
    penugasan_id: int,
    sasaran_id: str,
    payload: SasaranModePayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Anggota Tim memilih cara menyusun kertas kerja untuk sasarannya.

    Dipisahkan dari PUT sasaran-assignment (milik KT) karena pemiliknya beda:
    KT merencanakan sasaran & langkah kerja, AT memutuskan bagaimana kertas
    kerjanya disusun (analisis penuh AI · AI dari catatan auditor · manual).
    AT hanya boleh mengubah sasaran yang di-assign kepadanya; KT/PT boleh
    mengubah semuanya sebagai override supervisi.
    """
    user, role = current
    if role not in (Role.AT, Role.KT, Role.PT):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Role {role.value} tidak boleh mengubah cara penyusunan KKSA. Hanya AT (pelaksana) / KT / PT.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)

    path = Path(p.folder_path) / "_PKP" / "sasaran-assignment.json"
    if not path.exists():
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            "sasaran-assignment.json belum ada — Ketua Tim perlu menyimpan PKP dulu.",
        )
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            f"sasaran-assignment.json tidak bisa dibaca ({e}) — perubahan dibatalkan.",
        )

    target = next(
        (s for s in data.get("sasaran", []) if str(s.get("sasaran_id")) == sasaran_id),
        None,
    )
    if target is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, f"Sasaran '{sasaran_id}' tidak ditemukan."
        )

    # AT hanya boleh mengatur sasaran miliknya sendiri. `assigned_to` menyimpan
    # nama lengkap (dipakai KT saat assign lewat dropdown anggota).
    if role == Role.AT:
        assigned = [str(x).strip() for x in (target.get("assigned_to") or [])]
        if user.nama_lengkap.strip() not in assigned:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Sasaran '{sasaran_id}' tidak di-assign kepada Anda ({user.nama_lengkap}).",
            )

    sebelum = target.get("mode", "AI")
    target["mode"] = payload.mode
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "sasaran_id": sasaran_id,
        "mode": payload.mode,
        "mode_sebelumnya": sebelum,
    }


# ============================================================
# SIMWAS sync — terima PKP dari SIMWAS → sasaran-assignment.json
#
# W1.1 versi v7 (asli "agen baca KP/PKP PDF" sudah dibatalkan). Sekarang KT
# isi manual via tab Setup ATAU, untuk masa depan integrasi SIMWAS, frontend
# fetch PKP dari API SIMWAS lalu kirim ke endpoint ini sebagai `pkp_rows`.
# Hari ini dipakai dgn paste JSON manual (source='manual') — lihat fixture
# app/fixtures/simwas-sample-pkp.json. Saat API SIMWAS live, ganti ke
# source='api' (saat ini placeholder 501 sampai kontrak resmi tersedia).
# ============================================================


class SimwasPkpRow(BaseModel):
    """Satu baris PKP dari SIMWAS (1 langkah_kerja per baris pivot).

    Field-nya menebak struktur SIMWAS dari kartu "Detail Pelaksanaan Penugasan"
    tab PKP: kolom (sasaran, langkah_kerja, dilaksanakan_oleh, waktu, No KKP).
    `sasaran_id` opsional — kalau SIMWAS belum punya ID terpisah, kita auto-
    generate (`S-RKA-NN` / `S-PBJ-NN` / `S-NN`).
    """

    sasaran: str = Field(default="", description="Deskripsi sasaran reviu (jadi grouping key). Baris kosong di-skip.")
    langkah_kerja: str | None = Field(default=None, description="1 langkah per baris; di-aggregate per sasaran")
    dilaksanakan_oleh: str | None = Field(default=None, description="Nama anggota tim yg ditugaskan")
    waktu: str | None = Field(default=None, description="Periode kerja — disimpan untuk audit trail, tdk masuk sasaran-assignment")
    no_kkp: str | None = Field(default=None, description="Nomor KKP yg di-track SIMWAS — disimpan untuk audit trail")
    sasaran_id: str | None = Field(default=None, description="Opsional. Kalau SIMWAS punya, dipakai; kalau tidak, auto-generate.")


class SimwasSyncPayload(BaseModel):
    """Body POST /penugasan/{id}/sasaran/sync-from-simwas."""

    source: Literal["manual", "api"] = Field(
        default="manual",
        description="`manual` = paste JSON (testing hari ini). `api` = pull live dari SIMWAS (501 sampai integrasi resmi).",
    )
    strategy: Literal["replace", "append"] = Field(
        default="replace",
        description="`replace` = overwrite sasaran-assignment.json. `append` = tambahkan ke yang sudah ada (anti-dup by sasaran_id).",
    )
    pkp_rows: list[SimwasPkpRow]


def _generate_sasaran_id(prefix: str | None, counter: int) -> str:
    """Skill-aware ID: reviu-rka-kl → S-RKA-NN; reviu-pengadaan → S-PBJ-NN; lain → S-NN."""
    if prefix:
        return f"S-{prefix}-{counter:02d}"
    return f"S-{counter:02d}"


def _skill_prefix(skill_value: str) -> str | None:
    mapping = {
        "reviu-rka-kl": "RKA",
        "reviu-pengadaan": "PBJ",
        "audit-kinerja": "KIN",
        "audit-pengadaan": "PBJ",
        "pemantauan-pengadaan": "PBJ",
        "pemantauan-tindak-lanjut": "TL",
        "evaluasi-spip": "SPIP",
        "evaluasi-sakip": "SAKIP",
        "evaluasi-manajemen-risiko": "MR",
        "evaluasi-reformasi-birokrasi": "RB",
        "kepatuhan-saipi": "SAIPI",
        "konsultasi-pengadaan": "KONS",
    }
    return mapping.get(skill_value)


def pkp_rows_to_sasaran(
    rows: list[SimwasPkpRow],
    skill_value: str,
    existing_ids: set[str] | None = None,
) -> list[SasaranItem]:
    """Group flat PKP rows → SasaranItem records.

    Deterministik (no LLM). Aturan:
    - Grouping key = `sasaran_id` (kalau ada) else `sasaran` (deskripsi).
    - `langkah_kerja` di-dedup per sasaran (order-preserving).
    - `assigned_to` di-dedup per sasaran (order-preserving).
    - `sasaran_id` di-auto-generate per skill bila kosong; counter melompati
      `existing_ids` (penting untuk strategy='append' supaya tidak tabrakan
      dengan ID yang sudah ada di sasaran-assignment.json).
    - Status default `AKTIF`.
    - Baris dengan `sasaran` kosong di-skip (anti-junk).
    """
    groups: dict[str, dict] = {}
    order: list[str] = []
    for row in rows:
        key = (row.sasaran_id or row.sasaran or "").strip()
        if not key:
            continue
        if key not in groups:
            groups[key] = {
                "sasaran_id": (row.sasaran_id or "").strip() or None,
                "deskripsi": (row.sasaran or "").strip(),
                "assigned_to": [],
                "langkah_kerja": [],
            }
            order.append(key)
        g = groups[key]
        lk = (row.langkah_kerja or "").strip()
        if lk and lk not in g["langkah_kerja"]:
            g["langkah_kerja"].append(lk)
        ao = (row.dilaksanakan_oleh or "").strip()
        if ao and ao not in g["assigned_to"]:
            g["assigned_to"].append(ao)

    prefix = _skill_prefix(skill_value)
    used_ids: set[str] = set(existing_ids or set())
    result: list[SasaranItem] = []
    counter = 1
    for key in order:
        g = groups[key]
        sid = g["sasaran_id"]
        if not sid:
            while True:
                candidate = _generate_sasaran_id(prefix, counter)
                counter += 1
                if candidate not in used_ids:
                    sid = candidate
                    break
        used_ids.add(sid)
        result.append(
            SasaranItem(
                sasaran_id=sid,
                deskripsi=g["deskripsi"],
                assigned_to=g["assigned_to"],
                langkah_kerja=g["langkah_kerja"],
                status="AKTIF",
            )
        )
    return result


@router.post("/{penugasan_id}/sasaran/sync-from-simwas")
async def sync_sasaran_from_simwas(
    penugasan_id: int,
    payload: SimwasSyncPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Konversi PKP SIMWAS → `_PKP/sasaran-assignment.json`.

    PT/KT only. Default `source='manual'` (paste JSON; sah untuk test &
    bootstrap hari ini). `source='api'` masih 501 sampai kontrak REST/SSO
    SIMWAS resmi tersedia — saat itu frontend akan fetch PKP dari SIMWAS
    lalu mengirim ke endpoint ini dengan source='api' + token sesi.
    """
    user, role = current
    _require_sasaran_setup_role(role)

    if payload.source == "api":
        raise HTTPException(
            status.HTTP_501_NOT_IMPLEMENTED,
            "Pull live dari API SIMWAS belum aktif. Gunakan source='manual' "
            "(paste payload PKP). Akan hidup setelah kontrak API + SSO SIMWAS resmi.",
        )

    if not payload.pkp_rows:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "pkp_rows kosong — tidak ada yang di-sync.")

    p = await _get_penugasan_or_404(db, penugasan_id, current)
    skill_value = p.skill if isinstance(p.skill, str) else p.skill.value

    folder = Path(p.folder_path)
    path = folder / "_PKP" / "sasaran-assignment.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    # Pre-load existing IDs supaya converter melompati saat append (anti-tabrakan
    # auto-gen counter dgn ID yang sudah ada).
    existing_sasaran: list[dict] = []
    existing_ids: set[str] = set()
    if payload.strategy == "append" and path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
            existing_sasaran = existing.get("sasaran") or []
            existing_ids = {
                str(s.get("sasaran_id")) for s in existing_sasaran
                if isinstance(s, dict) and s.get("sasaran_id")
            }
        except (json.JSONDecodeError, OSError):
            existing_sasaran = []
            existing_ids = set()

    converted = pkp_rows_to_sasaran(payload.pkp_rows, skill_value, existing_ids=existing_ids)
    if not converted:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "Tidak ada sasaran valid setelah grouping — periksa field 'sasaran' di pkp_rows.",
        )

    if payload.strategy == "append":
        # Anti-dup berdasar sasaran_id explicit (yang muncul di PKP rows dgn ID).
        # Converter sudah memastikan auto-gen tidak tabrakan dgn existing_ids,
        # jadi yang bisa duplicate hanyalah sasaran_id eksplisit.
        final_sasaran = list(existing_sasaran)
        added_ids: list[str] = []
        for s in converted:
            if s.sasaran_id in existing_ids:
                continue
            final_sasaran.append(s.model_dump())
            added_ids.append(s.sasaran_id)
    else:
        final_sasaran = [s.model_dump() for s in converted]
        added_ids = [s.sasaran_id for s in converted]

    data = {
        "penugasan_id": p.kode,
        "skill": skill_value,
        "schema_version": "v4.0.0",
        "tanggal_dibuat": datetime.utcnow().isoformat() + "Z",
        "sasaran": final_sasaran,
        "sumber_import": f"simwas-{payload.source}",
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "source": payload.source,
        "strategy": payload.strategy,
        "total_input_rows": len(payload.pkp_rows),
        "total_sasaran": len(final_sasaran),
        "added_sasaran": added_ids,
        "added_count": len(added_ids),
        "skipped_duplicate": len(converted) - len(added_ids) if payload.strategy == "append" else 0,
    }


# ============================================================
# Setup template — saran sasaran dari penugasan lalu, skeleton pattern,
# & catatan W3 writeback. Tujuan: KT tidak mulai dari nol.
# ============================================================


@router.get("/{penugasan_id}/sasaran/templates")
async def get_sasaran_templates(
    penugasan_id: int,
    source: str = "all",  # all | historis | patterns | writeback
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Saran template setup penugasan dari 3 sumber paralel.

    - `historis`: penugasan v7 dgn skill sama, di-rank by similarity obyek
      (Jaccard atas token kata, stopword ID dibuang).
    - `patterns`: sasaran skeleton dari kategori pattern wiki — 1 sasaran per
      kategori, langkah_kerja merefer ID pattern dominan.
    - `writeback`: catatan `pengawasan-*.md` di vault llm-wiki (W3) yg related;
      ini KONTEKS, bukan sasaran (writeback tidak menyimpan sasaran eksplisit).

    `source='all'` (default) kembalikan ketiganya. Auditor PT/KT yg setup di
    UI memilih sumber + 1 entry, lalu pre-fill sasaran-assignment.json.
    """

    p = await _get_penugasan_or_404(db, penugasan_id, current)
    skill_value = p.skill if isinstance(p.skill, str) else p.skill.value
    obyek = p.obyek or ""

    result: dict[str, Any] = {
        "skill": skill_value,
        "obyek": obyek,
    }

    if source in ("all", "historis"):
        # Tarik semua penugasan lain (exclude self) untuk di-scan
        rows = (
            await db.execute(
                filter_penugasan(select(
                    Penugasan.kode,
                    Penugasan.obyek,
                    Penugasan.skill,
                    Penugasan.folder_path,
                    Penugasan.status,
                ).where(Penugasan.id != penugasan_id), current[0])
                # ISOLASI: jangan bocorkan penugasan Inspektorat lain
            )
        ).all()
        candidates = [
            {
                "kode": r[0],
                "obyek": r[1],
                "skill": r[2] if isinstance(r[2], str) else getattr(r[2], "value", str(r[2])),
                "folder_path": r[3],
                "status": r[4] if isinstance(r[4], str) else getattr(r[4], "value", str(r[4])),
            }
            for r in rows
        ]
        result["historis"] = _saran_historis(candidates, skill_value, obyek)



    return result


# ===========================================================================
# DAFTAR KRITERIA — khusus skill *-umum (criteria-driven)
#
# Skill umum tidak punya kriteria baku bawaan seperti reviu-rka-kl (PMK
# 107/2024) atau reviu-pengadaan (Perpres 16/2018); kriterianya datang dari
# auditor. Dua bentuk setara: berkas yang diunggah (dengan rujukan pasal), atau
# kriteria yang diketik langsung. Lihat app/daftar_kriteria.py.
# ===========================================================================


class RujukanKriteria(BaseModel):
    pasal: str = ""
    halaman: str = ""


class EntriKriteria(BaseModel):
    id: str | None = None
    tipe: str  # UNGGAHAN | KETIK
    file: str | None = None
    nama_file: str | None = None
    pindai: bool = False
    rujukan: list[RujukanKriteria] = Field(default_factory=list)
    sumber: str | None = None
    teks: str | None = None


class DaftarKriteriaPayload(BaseModel):
    entri: list[EntriKriteria] = Field(default_factory=list)


@router.get("/{penugasan_id}/daftar-kriteria")
async def get_daftar_kriteria(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Daftar kriteria + berkas kriteria yang tersedia. Semua role boleh baca."""
    from app import daftar_kriteria as dk
    from app.digest_generic import status_baca_berkas
    from app.skills_registry import is_skill_umum

    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    status_map = status_baca_berkas(folder)

    rows = (
        await db.execute(
            select(Dokumen).where(
                Dokumen.penugasan_id == p.id,
                Dokumen.jenis == "KRITERIA",
            )
        )
    ).scalars().all()
    berkas = []
    for d in rows:
        st = status_map.get((d.nama_file or "").strip().lower(), {})
        berkas.append({
            "dokumen_id": d.id,
            "nama_file": d.nama_file,
            "status": d.status.value if hasattr(d.status, "value") else str(d.status),
            "terbaca": st.get("terbaca"),
            "pindai": bool(st.get("pindai")),
            "rusak": bool(st.get("rusak")),
            "catatan_baca": st.get("catatan_baca") or d.error_message or "",
            "halaman_total": st.get("halaman_total") or 0,
        })

    return {
        "berlaku": is_skill_umum(p.skill),
        "ada_kriteria": dk.ada_kriteria(folder),
        "jumlah": dk.jumlah(folder),
        "entri": dk.ringkas(folder),
        "berkas_tersedia": berkas,
    }


@router.put("/{penugasan_id}/daftar-kriteria")
async def put_daftar_kriteria(
    penugasan_id: int,
    payload: DaftarKriteriaPayload,
    background_tasks: BackgroundTasks,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Simpan daftar kriteria. AT sebagai pelaksana; KT/PT boleh sebagai supervisi.

    Validasi sengaja KERAS pada dua hal, karena keduanya menentukan apakah agen
    bisa membaca kriteria sama sekali:
      - `pasal` WAJIB pada tiap rujukan — tanpa itu agen harus menyapu seluruh
        berkas (boros & sering meleset), yang justru ingin dihindari.
      - `halaman` WAJIB bila berkasnya hasil pindai — tulisan di gambar tak bisa
        dicari sebelum halamannya di-OCR, dan yang di-OCR ditentukan oleh
        halaman yang ditunjuk. Tanpa nomor halaman, berkas itu mustahil dibaca.
    """
    from app import daftar_kriteria as dk
    from app.digest_generic import status_baca_berkas

    user, role = current
    if role not in (Role.AT, Role.KT, Role.PT):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Daftar kriteria diisi Anggota Tim (AT); KT/PT boleh menyunting sebagai "
            f"supervisi. Role Anda: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    status_map = status_baca_berkas(folder)

    entri_bersih: list[dict[str, Any]] = []
    nomor = 0
    for e in payload.entri:
        tipe = (e.tipe or "").strip().upper()
        nomor += 1
        eid = (e.id or "").strip() or f"K-{nomor:03d}"
        if tipe == dk.TIPE_KETIK:
            teks = (e.teks or "").strip()
            if not teks:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"Kriteria {eid}: teks kriteria masih kosong.",
                )
            entri_bersih.append({
                "id": eid, "tipe": dk.TIPE_KETIK,
                "sumber": (e.sumber or "").strip(), "teks": teks,
            })
            continue

        if tipe != dk.TIPE_UNGGAHAN:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Kriteria {eid}: tipe '{e.tipe}' tidak dikenal (UNGGAHAN atau KETIK).",
            )
        berkas = (e.file or e.nama_file or "").strip()
        if not berkas:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"Kriteria {eid}: berkas kriteria belum dipilih.",
            )
        nama = Path(berkas.replace("\\", "/")).name
        st = status_map.get(nama.strip().lower(), {})
        if st.get("rusak"):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"{nama} tidak bisa dibaca sistem (berkas rusak atau format tak didukung). "
                "Menyebut nomor halaman tidak menolong — unggah ulang versi yang bisa dibuka.",
            )
        pindai = bool(st.get("pindai", e.pindai))
        rujukan = [r for r in e.rujukan if (r.pasal or "").strip() or (r.halaman or "").strip()]
        if not rujukan:
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                f"{nama}: sebutkan minimal satu pasal/bagian yang dipakai — agen hanya "
                "membaca bagian itu, bukan seluruh berkas.",
            )
        bersih_rujukan = []
        for r in rujukan:
            pasal = (r.pasal or "").strip()
            halaman = (r.halaman or "").strip()
            if not pasal:
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"{nama}: nomor pasal/bagian wajib diisi pada setiap rujukan.",
                )
            if pindai and not dk.parse_halaman(halaman):
                raise HTTPException(
                    status.HTTP_422_UNPROCESSABLE_ENTITY,
                    f"{nama} adalah berkas hasil pindai — sebutkan nomor halaman untuk "
                    f"'{pasal}' agar bisa dibaca sistem.",
                )
            bersih_rujukan.append({"pasal": pasal, "halaman": halaman})
        entri_bersih.append({
            "id": eid, "tipe": dk.TIPE_UNGGAHAN, "file": berkas,
            "nama_file": nama, "pindai": pindai, "rujukan": bersih_rujukan,
        })

    dk.write(folder, {"versi": 1, "entri": entri_bersih})
    append_audit_trail(folder, {
        "event": "daftar_kriteria_disimpan",
        "oleh": user.nama_lengkap,
        "role": role.value,
        "jumlah": len(entri_bersih),
    })

    # Halaman yang baru ditunjuk perlu di-OCR supaya benar-benar terbaca. Tanpa
    # ini, menunjuk halaman tak berefek apa pun sampai ada unggahan berikutnya.
    from app.routes.dokumen import _ingest_background

    background_tasks.add_task(_ingest_background, p.id)

    return {
        "ok": True,
        "jumlah": len(entri_bersih),
        "ada_kriteria": dk.ada_kriteria(folder),
        "entri": dk.ringkas(folder),
    }


@router.get("/{penugasan_id}/context-readiness")
async def get_context_readiness(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Prasyarat tombol Generate Context: sasaran (KT) + bahan analisis (AT).

    Bahan = dokumen ter-digest (RKA/PBJ) atau kriteria/objek (criteria-driven).
    """
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    input_jenis = (
        await db.execute(
            select(Dokumen.jenis).where(
                Dokumen.penugasan_id == p.id,
                Dokumen.status == DokumenStatus.READY,
            )
        )
    ).scalars().all()
    has_input = any((j or "").upper() in INPUT_JENIS for j in input_jenis)
    return context_readiness(Path(p.folder_path), skill=p.skill, has_input_docs=has_input)


@router.get("/{penugasan_id}/context-md")
async def get_context_md(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Read isi context.md — bisa diakses semua role."""
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    path = Path(p.folder_path) / "context.md"
    if not path.exists():
        return {"content": "", "exists": False}
    return {
        "content": path.read_text(encoding="utf-8"),
        "exists": True,
    }


class ContextMdPayload(BaseModel):
    content: str = Field(..., description="Isi context.md raw markdown")


@router.put("/{penugasan_id}/context-md")
async def put_context_md(
    penugasan_id: int,
    payload: ContextMdPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Overwrite context.md — KT/PT setup awal, AT untuk penyempurnaan saat analisis."""
    user, role = current
    _require_context_edit_role(role)
    p = await _get_penugasan_or_404(db, penugasan_id, current)

    path = Path(p.folder_path) / "context.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload.content, encoding="utf-8")

    return {
        "ok": True,
        "size_bytes": len(payload.content.encode("utf-8")),
        "path": "context.md",
    }


# ============================================================
# Kartu Penugasan (KP) — diisi PT (tahapan 1), dokumen administratif.
# Beda dgn context.md (konteks kerja AI yang di-generate AT). Disimpan sbg
# _KP/kartu-penugasan.md. Diisi dari template wiki (kind=kp) lalu di-edit.
# ============================================================

_KP_REL = "_KP/kartu-penugasan.md"
_KP_FIELDS_REL = "_KP/kp-fields.json"


class KpPayload(BaseModel):
    content: str = Field(..., description="Isi Kartu Penugasan (markdown ter-render)")
    # Nilai field form terstruktur — format INTEGRAL (hasil bedah form live
    # simwasv2 10 Jun 2026): nomor, judul, dasar, aktivitas_tingkat_risiko,
    # tujuan, ruang_lingkup, tanggal, disusun_oleh.
    # Disimpan terpisah supaya form bisa di-reedit tanpa parse markdown.
    fields: dict[str, str] | None = None
    # Daftar Sasaran Pengawasan (repeatable di form KP INTEGRAL). Saat simpan,
    # otomatis di-sync ke _PKP/sasaran-assignment.json — meniru INTEGRAL di mana
    # bagian "II. Pelaksanaan" PKP dibangun dari sasaran KP.
    sasaran: list[str] | None = None
    # Slug template wiki yang dipakai (kosong = isi manual tanpa template).
    template_slug: str | None = None


@router.get("/{penugasan_id}/kp-md")
async def get_kp_md(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Read Kartu Penugasan: markdown + nilai field form — semua role bisa baca."""
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    path = folder / _KP_REL
    fields_path = folder / _KP_FIELDS_REL
    fields: dict | None = None
    sasaran: list | None = None
    template_slug: str | None = None
    if fields_path.exists():
        try:
            raw = json.loads(fields_path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                fields = raw.get("fields")
                sasaran = raw.get("sasaran")
                template_slug = raw.get("template_slug")
        except (json.JSONDecodeError, OSError):
            fields = None
    if not path.exists():
        return {"content": "", "exists": False, "fields": fields, "sasaran": sasaran, "template_slug": template_slug}
    return {
        "content": path.read_text(encoding="utf-8"),
        "exists": True,
        "fields": fields,
        "sasaran": sasaran,
        "template_slug": template_slug,
    }


@router.put("/{penugasan_id}/kp-md")
async def put_kp_md(
    penugasan_id: int,
    payload: KpPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Overwrite Kartu Penugasan (markdown + field form). Hanya PT/KT."""
    _user, role = current
    if role not in (Role.PT, Role.KT):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Kartu Penugasan diisi oleh Pengendali Teknis (PT)/Ketua Tim (KT). Role Anda: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    path = folder / _KP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload.content, encoding="utf-8")
    # Tulis juga dokumen KP ke 00-input/ supaya QC SAIPI REN-001 (SAIPI 2200:
    # "KP tersedia di 00-input/") terpenuhi. INTEGRAL: KP berasal dari sistem,
    # di-drop sebagai dokumen 00-input/. Nama harus cocok glob `KP-*.*`.
    kp_doc = folder / "00-input" / f"KP-{p.kode}.md"
    kp_doc.parent.mkdir(parents=True, exist_ok=True)
    kp_doc.write_text(payload.content, encoding="utf-8")
    # v10.1 (transplant tahapan v8): KP tersimpan → sentinel KP_DONE → unlock PKP.
    _kp_flag = folder / "_PKP" / "kp-saved.flag"
    _kp_flag.parent.mkdir(parents=True, exist_ok=True)
    if not _kp_flag.exists():
        _kp_flag.write_text("saved", encoding="utf-8")
    if payload.fields is not None or payload.sasaran is not None:
        (folder / _KP_FIELDS_REL).write_text(
            json.dumps(
                {
                    "fields": payload.fields or {},
                    "sasaran": payload.sasaran or [],
                    "template_slug": payload.template_slug,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    # Sync sasaran KP → _PKP/sasaran-assignment.json (meniru INTEGRAL: PKP
    # bagian "II. Pelaksanaan" dibangun dari sasaran Kartu Penugasan).
    # Append-only by deskripsi — baris existing (beserta langkah/assignment)
    # tidak disentuh; sasaran KP yang dihapus TIDAK menghapus baris PKP.
    synced = 0
    if payload.sasaran:
        sa_path = folder / "_PKP" / "sasaran-assignment.json"
        try:
            data = json.loads(sa_path.read_text(encoding="utf-8")) if sa_path.exists() else {}
        except (json.JSONDecodeError, OSError):
            data = {}
        if not isinstance(data, dict):
            data = {}
        rows = data.get("sasaran") or []
        existing_desc = {str(r.get("deskripsi", "")).strip().lower() for r in rows if isinstance(r, dict)}
        for desc in payload.sasaran:
            d = str(desc).strip()
            if not d or d.lower() in existing_desc:
                continue
            rows.append({
                "sasaran_id": f"S-{len(rows) + 1:02d}",
                "deskripsi": d,
                "assigned_to": [],
                "langkah_kerja": [],
                "status": "AKTIF",
                "waktu": "",
                "no_kkp": "",
            })
            existing_desc.add(d.lower())
            synced += 1
        if synced:
            data.setdefault("penugasan_id", p.kode)
            data.setdefault("skill", p.skill if isinstance(p.skill, str) else p.skill.value)
            data.setdefault("schema_version", "v4.0.0")
            data["sasaran"] = rows
            sa_path.parent.mkdir(parents=True, exist_ok=True)
            sa_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return {
        "ok": True,
        "size_bytes": len(payload.content.encode("utf-8")),
        "path": _KP_REL,
        "sasaran_synced_to_pkp": synced,
    }


# ============================================================
# Preload Context Bundle (Prioritas 1 — peningkatan kualitas)
# Bangun konteks 4-sumber sebelum agen jalan supaya agen mulai dgn tangan penuh.
# ============================================================


@router.get("/{penugasan_id}/temuan-review")
async def list_temuan_review(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """List semua temuan + status review (semua role bisa baca)."""
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    temuan_list = _load_temuan_json(folder)

    # Ambil semua review row utk penugasan ini
    rows = (
        await db.execute(select(TemuanReview).where(TemuanReview.penugasan_id == penugasan_id))
    ).scalars().all()
    by_temuan_id: dict[str, TemuanReview] = {r.temuan_id: r for r in rows}

    items: list[dict] = []
    for t in temuan_list:
        if not isinstance(t, dict):
            continue
        tid = str(t.get("id_temuan") or "").strip()
        if not tid:
            continue
        rev = by_temuan_id.get(tid)
        # Apply overlay edit kalau ada — tampilkan versi terkini ke UI
        edited = rev.edited_fields if rev and rev.edited_fields else {}
        judul = edited.get("judul_temuan") or t.get("judul_temuan") or ""
        kondisi = edited.get("kondisi") or t.get("kondisi") or ""
        kriteria = edited.get("kriteria") or t.get("kriteria") or ""
        sebab = edited.get("sebab") or t.get("sebab") or ""
        akibat = edited.get("akibat") or t.get("akibat") or ""
        # dokumen_sumber ikut bisa diedit auditor → hitung dari versi TERKINI,
        # bukan versi agen, supaya indikator di UI tidak menyesatkan.
        ds_efektif = edited.get("dokumen_sumber")
        if not isinstance(ds_efektif, list):
            ds_efektif = t.get("dokumen_sumber")
        items.append({
            "id_temuan": tid,
            "judul": judul,
            "sasaran_id": t.get("sasaran_id") or "",
            "ro": str(t.get("ro") or "").strip(),  # label RO (RKA-K/L multi-RO); kosong = non-RKA/RO tunggal
            # AI · AI_DARI_CATATAN · MANUAL — penentu apakah label "draf AI" pantas dipasang.
            "origin": str(t.get("origin") or "AI").strip() or "AI",
            "kondisi": kondisi[:400],
            "kriteria": kriteria[:400],
            "sebab": sebab[:400],
            "akibat": akibat[:400],
            "anggota": ((t.get("anggota_tim") or {}).get("nama_lengkap") or "") if isinstance(t.get("anggota_tim"), dict) else "",
            "dokumen_sumber": ds_efektif if isinstance(ds_efektif, list) else [],
            "dokumen_sumber_count": len(ds_efektif) if isinstance(ds_efektif, list) else 0,
            "status": rev.status if rev else "PENDING",
            "note": rev.note if rev else None,
            "reviewed_at": rev.reviewed_at.isoformat() + "Z" if rev and rev.reviewed_at else None,
            "reviewed_by_user_id": rev.reviewed_by_user_id if rev else None,
            "has_edits": bool(edited),
            "edited_fields": edited or None,  # full edit overlay (UI bisa pakai untuk diff/preview)
            "edit_log": (rev.edit_log if rev else None) or [],  # riwayat edit manual
        })

    counts = {"PENDING": 0, "APPROVED": 0, "REJECTED": 0, "EDITED": 0}
    for i in items:
        counts[i["status"]] = counts.get(i["status"], 0) + 1
    return {"total": len(items), "counts": counts, "items": items}


_LKE_SKILLS = {"evaluasi-sakip", "evaluasi-spip", "evaluasi-reformasi-birokrasi"}


@router.get("/{penugasan_id}/penilaian-lke")
async def get_penilaian_lke(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Rekap penilaian LKE (skor/predikat per unsur) untuk penugasan evaluasi
    ber-LKE. `is_lke=False` bila skill bukan rezim LKE atau rekap belum ada —
    UI pakai flag ini untuk memilih tampilan (rekap+AoI vs KKSA biasa)."""
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    skill = p.skill if isinstance(p.skill, str) else getattr(p.skill, "value", str(p.skill))
    is_lke_skill = skill in _LKE_SKILLS
    folder = Path(p.folder_path)
    src = folder / "_KKP" / f"penilaian-lke-{skill}.json"
    if not src.is_file():
        # fallback: glob apa pun penilaian-lke-*.json (skill mungkin tak persis)
        src = next(iter(sorted((folder / "_KKP").glob("penilaian-lke-*.json"))), None)
    if not is_lke_skill or not src or not src.is_file():
        return {"is_lke": is_lke_skill, "skill": skill, "tersedia": False,
                "komponen": [], "total_pm": None, "total_apip": None, "predikat_akhir": None}
    try:
        pen = json.loads(src.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"is_lke": True, "skill": skill, "tersedia": False, "komponen": [],
                "total_pm": None, "total_apip": None, "predikat_akhir": None}
    komp = pen.get("komponen") or []
    # Normalisasi ringan + hitung selisih PM-APIP per unsur.
    out_komp = []
    for k in komp if isinstance(komp, list) else []:
        if not isinstance(k, dict):
            continue
        pm, apip = k.get("nilai_pm"), k.get("nilai_apip")
        try:
            delta = round(float(pm) - float(apip), 2) if pm not in (None, "") and apip not in (None, "") else None
        except (TypeError, ValueError):
            delta = None
        out_komp.append({
            "nama": k.get("nama", ""), "bobot": k.get("bobot"),
            "nilai_pm": pm, "nilai_apip": apip, "delta": delta,
            "predikat": k.get("predikat", ""), "catatan": k.get("catatan"),
        })
    return {
        "is_lke": True, "skill": skill, "tersedia": True,
        "komponen": out_komp,
        "total_pm": pen.get("total_pm"),
        "total_apip": pen.get("total_apip") or pen.get("nilai_akhir"),
        "predikat_akhir": pen.get("predikat_akhir") or pen.get("predikat"),
    }


class TemuanReviewAction(BaseModel):
    note: str | None = None


@router.post("/{penugasan_id}/temuan-review/{temuan_id}/approve")
async def approve_temuan(
    penugasan_id: int,
    temuan_id: str,
    payload: TemuanReviewAction = Body(default_factory=TemuanReviewAction),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Setujui temuan — masuk ke KKP/LHR final. AT/KT/PT boleh."""
    user, role = current
    if role not in (Role.AT, Role.KT, Role.PT, Role.PM):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Role {role.value} tidak bisa approve.")
    await _get_penugasan_or_404(db, penugasan_id, current)
    return await _upsert_review(db, penugasan_id, temuan_id, "APPROVED", payload.note, user.id)


@router.post("/{penugasan_id}/temuan-review/{temuan_id}/reject")
async def reject_temuan(
    penugasan_id: int,
    temuan_id: str,
    payload: TemuanReviewAction = Body(default_factory=TemuanReviewAction),
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Tolak temuan — tidak masuk KKP/LHR. KT/PT/PM only."""
    user, role = current
    if role not in (Role.KT, Role.PT, Role.PM):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Tolak temuan hanya untuk KT/PT/PM. Role: {role.value}.",
        )
    await _get_penugasan_or_404(db, penugasan_id, current)
    return await _upsert_review(db, penugasan_id, temuan_id, "REJECTED", payload.note, user.id)


class TemuanEditPayload(BaseModel):
    """Field temuan yang bisa diedit auditor via UI.

    Semua optional — hanya field yang dikirim yang di-overlay. Field lain
    tetap pakai versi agen di temuan.json.

    `sebab` + `dokumen_sumber` + kodefikasi ditambahkan 4 Agu 2026: sebelumnya
    hanya judul/kondisi/kriteria/akibat yang bisa diedit, sehingga ketika agen
    menulis Sebab = "tidak cukup data" (persis yang dituntut doktrin
    anti-mengarang), auditor yang KEMUDIAN menemukan penyebabnya tidak punya
    jalan untuk melengkapinya. Ketiganya juga field yang diperiksa QC SAIPI
    (KKP-004 dokumen_sumber, KKP-006 halaman, KKP-010 sebab).
    """
    judul_temuan: str | None = None
    kondisi: str | None = None
    kriteria: str | None = None
    sebab: str | None = None
    akibat: str | None = None
    # [{"file": "02-kontrak/KAK.pdf", "halaman": 3, "kutipan": "..."}]
    dokumen_sumber: list[dict] | None = None
    kode_kondisi: str | None = None
    kode_penyebab: str | None = None
    kode_rekomendasi: str | None = None
    note: str | None = None  # catatan kenapa diedit


@router.put("/{penugasan_id}/temuan-review/{temuan_id}/edit")
async def edit_temuan(
    penugasan_id: int,
    temuan_id: str,
    payload: TemuanEditPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Edit field temuan via overlay (judul/kondisi/kriteria/akibat). AT/KT/PT/PM.

    Strategi: temuan.json (sumber kebenaran V6) TIDAK diubah. Edit disimpan di
    `TemuanReview.edited_fields` (JSONB). Saat render KKP, v7 overlay edited_fields
    ke temuan asli sebelum panggil V6.

    Status auto-set ke "EDITED" (tetap masuk render bersama APPROVED). Auditor bisa
    re-approve/reject kapan saja setelah edit.

    Field yang KOSONG di payload → tidak ubah overlay (tidak hapus edit lama).
    Untuk hapus edit field tertentu, kirim string kosong eksplisit "".
    """
    user, role = current
    if role not in (Role.AT, Role.KT, Role.PT, Role.PM):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Edit temuan hanya untuk AT/KT/PT/PM. Role: {role.value}.",
        )
    await _get_penugasan_or_404(db, penugasan_id, current)

    # Verifikasi temuan ada di temuan.json
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    temuan_list = _load_temuan_json(folder)
    found = next(
        (t for t in temuan_list if isinstance(t, dict) and str(t.get("id_temuan") or "").strip() == temuan_id),
        None,
    )
    if found is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Temuan {temuan_id} tidak ditemukan di temuan.json.",
        )

    # Upsert review row
    existing = (
        await db.execute(
            select(TemuanReview).where(
                TemuanReview.penugasan_id == penugasan_id,
                TemuanReview.temuan_id == temuan_id,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        existing = TemuanReview(
            penugasan_id=penugasan_id,
            temuan_id=temuan_id,
            status="EDITED",
            edited_fields={},
        )
        db.add(existing)
        await db.flush()

    # Merge edits (existing edited_fields + new payload) + rekam LOG perubahan.
    edits: dict = dict(existing.edited_fields or {})
    payload_dict = payload.model_dump(exclude_none=True, exclude={"note"})
    changes: dict[str, dict] = {}
    for k, v in payload_dict.items():
        # Sentinel "revert ke versi agen": "" untuk field teks, [] untuk dokumen_sumber.
        is_revert = (v == "" or v == [])
        # Nilai lama efektif = overlay sebelumnya bila ada, else versi agen di temuan.json.
        old_v = edits.get(k, found.get(k, ""))
        new_v = (found.get(k, "") if is_revert else v)
        if str(old_v).strip() != str(new_v).strip():
            changes[k] = {"from": (str(old_v)[:300] or "(kosong)"), "to": (str(new_v)[:300] or "(kosong)")}
        if is_revert:
            edits.pop(k, None)
        else:
            edits[k] = v

    existing.edited_fields = edits or None
    existing.status = "EDITED" if edits else "PENDING"
    if payload.note is not None:
        existing.note = payload.note
    existing.reviewed_by_user_id = user.id
    existing.reviewed_at = datetime.utcnow()

    # Append-only edit log (akuntabilitas — setiap edit manual direkam).
    if changes:
        log = list(existing.edit_log or [])
        log.append({
            "at": datetime.utcnow().isoformat() + "Z",
            "by_user_id": user.id,
            "by_nama": user.nama_lengkap,
            "by_role": role.value,
            "changes": changes,
            "note": (payload.note or None),
        })
        existing.edit_log = log
    await db.commit()

    return {
        "ok": True,
        "id_temuan": temuan_id,
        "status": existing.status,
        "edited_fields": existing.edited_fields,
        "has_edits": bool(existing.edited_fields),
        "reviewed_at": existing.reviewed_at.isoformat() + "Z" if existing.reviewed_at else None,
    }


@router.post("/{penugasan_id}/temuan-review/bulk-approve")
async def bulk_approve_temuan(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Setujui SEMUA temuan PENDING sekaligus — efisiensi auditor senior."""
    user, role = current
    if role not in (Role.KT, Role.PT, Role.PM):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Bulk approve hanya untuk KT/PT/PM. Role: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    temuan_list = _load_temuan_json(folder)
    rows = (
        await db.execute(select(TemuanReview).where(TemuanReview.penugasan_id == penugasan_id))
    ).scalars().all()
    by_temuan_id = {r.temuan_id: r for r in rows}

    n_approved = 0
    for t in temuan_list:
        tid = str(t.get("id_temuan") or "").strip()
        if not tid:
            continue
        existing = by_temuan_id.get(tid)
        if existing and existing.status == "APPROVED":
            continue  # already approved
        if existing:
            existing.status = "APPROVED"
            existing.reviewed_by_user_id = user.id
            existing.reviewed_at = datetime.utcnow()
        else:
            db.add(TemuanReview(
                penugasan_id=penugasan_id,
                temuan_id=tid,
                status="APPROVED",
                reviewed_by_user_id=user.id,
                reviewed_at=datetime.utcnow(),
            ))
        n_approved += 1
    await db.commit()
    return {"ok": True, "approved_count": n_approved, "total_temuan": len(temuan_list)}


@router.post("/{penugasan_id}/kkp/submit")
async def submit_kkp_to_kt(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Submit KKP ke Ketua Tim (Anggota Tim).

    Model HITL baru: tidak ada approve/tolak per-temuan. AT mengkurasi temuan
    via EDIT manual (terekam log) + iterasi chat, lalu menekan SUBMIT untuk
    mengajukan sasaran yang ditugaskan kepadanya ke KT untuk direview/disetujui.

    Efek: sasaran milik AT (assigned_to memuat namanya) ditandai `SELESAI_KKP`
    + `diajukan_oleh`/`diajukan_pada` (akuntabilitas). KT lalu menyetujui di Tahapan 4.
    """
    user, role = current
    if role != Role.AT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Submit KKP hanya untuk Anggota Tim. Role: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    sa_path = folder / "_PKP" / "sasaran-assignment.json"
    if not sa_path.exists():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "sasaran-assignment.json belum ada.")
    try:
        data = json.loads(sa_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "sasaran-assignment.json corrupt.")

    # Ketertelusuran sasaran → temuan (QC SAIPI LAK-009 / SAIPI 2310.A1).
    # Diturunkan dari `sasaran_id` pada tiap temuan, bukan diisi manual: tidak
    # ada satu pun jalur di v7 yang pernah menulis `id_temuan_terkait`, sehingga
    # LAK-009 selalu menyala di SEMUA penugasan — baik temuan bikinan agen
    # maupun KKSA manual. Berlaku sama untuk ketiga skema penyusunan.
    temuan_per_sasaran: dict[str, list[str]] = {}
    for t in _load_temuan_json(folder):
        if not isinstance(t, dict):
            continue
        sid = str(t.get("sasaran_id") or "").strip()
        tid = str(t.get("id_temuan") or "").strip()
        if sid and tid:
            temuan_per_sasaran.setdefault(sid, []).append(tid)

    nama = (user.nama_lengkap or "").strip().lower()
    now = datetime.utcnow().isoformat() + "Z"
    sasaran = data.get("sasaran", []) if isinstance(data, dict) else []
    submitted: list[str] = []
    for s in sasaran:
        if not isinstance(s, dict):
            continue
        assigned = {str(a).strip().lower() for a in (s.get("assigned_to") or [])}
        if nama and nama in assigned:
            # Jangan downgrade keputusan KT yang sudah ada.
            if s.get("status") in (None, "", "AKTIF", "SELESAI_KKP"):
                s["status"] = "SELESAI_KKP"
            s["diajukan_oleh"] = user.nama_lengkap
            s["diajukan_pada"] = now
            # Kosong dibiarkan kosong — sasaran tanpa temuan memang harus
            # dinyatakan eksplisit oleh auditor, bukan ditutupi isian palsu.
            terkait = temuan_per_sasaran.get(str(s.get("sasaran_id") or "").strip(), [])
            if terkait:
                s["id_temuan_terkait"] = terkait
            submitted.append(str(s.get("sasaran_id") or ""))

    sa_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # v10.1 (transplant tahapan v8): bila SEMUA sasaran ber-assigned_to sudah
    # SELESAI_KKP/DISETUJUI_KT → tulis kkp-at-done.flag → status KKP_AT_DONE
    # (AT selesai, menunggu persetujuan per-sasaran oleh KT di Tahapan 4).
    _sasaran_all = data.get("sasaran", []) if isinstance(data, dict) else []
    _assigned = [s for s in _sasaran_all if isinstance(s, dict) and s.get("assigned_to")]
    _all_at_done = bool(_assigned) and all(
        s.get("status") in ("SELESAI_KKP", "DISETUJUI_KT") for s in _assigned
    )
    if _all_at_done:
        _at_flag = folder / "_KKP" / "kkp-at-done.flag"
        _at_flag.parent.mkdir(parents=True, exist_ok=True)
        _at_flag.write_text(f"done at {now}", encoding="utf-8")

    return {
        "ok": True,
        "submitted_count": len(submitted),
        "sasaran": submitted,
        "kkp_at_done": bool(_all_at_done),
        "message": (
            f"{len(submitted)} sasaran diajukan ke Ketua Tim untuk direview."
            if submitted else
            "Tidak ada sasaran yang ditugaskan kepada Anda untuk disubmit."
        ),
    }


@router.put("/{penugasan_id}/pkp/approve")
async def approve_pkp(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """PT menyetujui PKP setelah KT mengisi sasaran (transplant tahapan v8 → v10.1).

    Efek: tulis _PKP/pkp-pt-approved.flag → status PKP_DONE → tahap KKP terbuka.
    (Persetujuan KKP tetap per-sasaran via SasaranApprovalPanel — bukan LRS-KK.)
    """
    user, role = current
    if role != Role.PT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Hanya Pengendali Teknis (PT) yang dapat menyetujui PKP.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    if not (folder / "_PKP" / "pkp-kt-saved.flag").exists():
        # Compat: cek juga sasaran-assignment.json punya sasaran
        pkp_file = folder / "_PKP" / "sasaran-assignment.json"
        has_sasaran = False
        if pkp_file.exists():
            try:
                sa = json.loads(pkp_file.read_text(encoding="utf-8"))
                has_sasaran = isinstance(sa, dict) and bool(sa.get("sasaran"))
            except (json.JSONDecodeError, OSError):
                pass
        if not has_sasaran:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "PKP belum diisi oleh Ketua Tim. Minta KT mengisi sasaran terlebih dahulu.",
            )
    flag = folder / "_PKP" / "pkp-pt-approved.flag"
    flag.write_text(
        f"approved by {user.nama_lengkap} at {datetime.utcnow().isoformat()}Z",
        encoding="utf-8",
    )
    return {"ok": True, "message": "PKP disetujui. Tahap KKP sudah terbuka untuk tim."}


class TemuanManualPayload(BaseModel):
    """KKSA yang ditulis auditor sendiri, tanpa agen (skema 3 — mode manual).

    Doktrin TIDAK dilonggarkan di mode manual: `dokumen_sumber` tetap wajib
    (kutipan sumber), dan `sebab` yang belum terbukti diisi apa adanya
    ("tidak cukup data") — bukan dikarang, bukan pula dibiarkan kosong diam-diam.
    """
    sasaran_id: str = Field(..., min_length=1)
    judul_temuan: str = Field(..., min_length=1)
    kondisi: str = Field(..., min_length=1)
    kriteria: str = Field(..., min_length=1)
    akibat: str = Field(..., min_length=1)
    # OPSIONAL sejak 9 Agu 2026 (keputusan pemilik proses).
    #
    # Sebelumnya wajib >=1 entri ber-`file`+`halaman`, mengikuti QC SAIPI LAK-001
    # & LAK-003. Aturan itu dicabut KHUSUS jalur manual: temuan yang ditulis
    # auditor sendiri diperiksa sendiri oleh auditor ("temuan manual = semua
    # manual"), sehingga sistem tidak lagi menghalangi penyimpanan.
    #
    # Konsekuensi yang ditangani di tempat lain: `run_qc_kkp` mengecualikan
    # temuan ber-`origin=MANUAL` dari QC SAIPI otomatis — kalau tidak, LAK-001
    # (severity KRITIS) akan menandai setiap temuan manual sebagai gap. Skrip QC
    # ada di V6 yang read-only, jadi pengecualian dikerjakan di lapisan aplikasi.
    #
    # Bila auditor TETAP mengisi (dianjurkan), bentuknya masih divalidasi supaya
    # entri setengah jadi tidak masuk diam-diam.
    dokumen_sumber: list[dict] = Field(default_factory=list)
    sebab: str | None = None
    kode_kondisi: str | None = None
    kode_penyebab: str | None = None
    kode_rekomendasi: str | None = None
    langkah_kerja_terkait: str | None = None
    ro: str | None = None


@router.post("/{penugasan_id}/temuan", status_code=status.HTTP_201_CREATED)
async def create_temuan_manual(
    penugasan_id: int,
    payload: TemuanManualPayload,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Tulis 1 temuan KKSA MANUAL — tanpa agen. Anggota Tim saja.

    Melengkapi dua mode yang sudah ada (AI dari dokumen · AI dari catatan
    auditor) menjadi tiga skema; gerbang sesudahnya identik — SUBMIT lalu
    reviu berjenjang ke Ketua Tim.

    Memakai `_normalize_temuan_input` + `next_temuan_id` yang sama dengan tool
    agen, jadi penomoran T-NNN tidak pernah bertabrakan antara temuan manual
    dan temuan bikinan agen dalam satu penugasan.
    """
    user, role = current
    if role != Role.AT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Menulis KKSA manual hanya untuk Anggota Tim. Role Anda: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)

    # Dokumen sumber OPSIONAL di jalur manual (keputusan 9 Agu 2026): temuan yang
    # ditulis auditor sendiri diperiksa sendiri oleh auditor. Yang dulu ditolak
    # keras di sini sekarang cuma dirapikan — entri kosong dibuang supaya tidak
    # ada baris hampa masuk ke temuan.json.
    #
    # Ini BUKAN pintu belakang menembus QC: `run_qc_kkp`/`run_qc_lhp` tetap
    # menjalankan QC SAIPI penuh, hanya mengecualikan temuan ber-origin MANUAL
    # dari LAK-001/LAK-003 dan MENCATAT pengecualian itu di laporan QC.
    # Lihat app/qc_exempt.py.
    dokumen_sumber_bersih: list[dict] = []
    for ds in payload.dokumen_sumber:
        if not isinstance(ds, dict):
            continue
        berkas = str(ds.get("file") or "").strip()
        halaman = ds.get("halaman")
        kutipan = str(ds.get("kutipan") or "").strip()
        if not berkas and not kutipan:
            continue  # baris kosong dari formulir — abaikan diam-diam
        entri: dict[str, Any] = {"file": berkas}
        if halaman not in (None, ""):
            entri["halaman"] = halaman
        if kutipan:
            entri["kutipan"] = kutipan
        dokumen_sumber_bersih.append(entri)
    payload.dokumen_sumber = dokumen_sumber_bersih

    folder = Path(p.folder_path)
    temuan_path = folder / "_KKP" / "temuan.json"
    temuan_path.parent.mkdir(parents=True, exist_ok=True)
    if temuan_path.exists():
        try:
            data = json.loads(temuan_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                f"temuan.json tidak bisa dibaca ({e}) — penulisan dibatalkan agar temuan lama tidak tertimpa.",
            )
    else:
        data = {}
    if not isinstance(data, dict) or "temuan" not in data:
        data = {
            "penugasan": {
                "kode": p.kode,
                "obyek": p.obyek,
                "jenis_pengawasan": p.skill if isinstance(p.skill, str) else p.skill.value,
                "nomor_st": p.nomor_st or "",
                "tanggal_st": p.tanggal_st,
            },
            "schema_version": "v4.0.0",
            "temuan": [],
        }
    data.setdefault("temuan", [])

    from app.tools.kkp_tools import _normalize_temuan_input, next_temuan_id

    baru = _normalize_temuan_input({
        **payload.model_dump(exclude_none=True),
        "anggota_tim": {"nama_lengkap": user.nama_lengkap},
        "origin": "MANUAL",
    })
    baru["id_temuan"] = next_temuan_id(data["temuan"])
    data["temuan"].append(baru)

    tmp = temuan_path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, temuan_path)

    return {
        "ok": True,
        "id_temuan": baru["id_temuan"],
        "origin": "MANUAL",
        "total_temuan": len(data["temuan"]),
    }


@router.post("/{penugasan_id}/kkp/render")
async def render_kkp(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Render `_KKP/KKP-{nama}.docx` tanpa memanggil agen. Anggota Tim saja.

    Diperlukan mode KKSA MANUAL (skema 3): di sana tidak ada sesi agen sama
    sekali, sedangkan render selama ini hanya bisa lewat tool agen — sehingga
    QC SAIPI LAK-007 (wajib ada KKP-*.docx) mustahil dipenuhi.

    Memanggil inti yang SAMA dengan tool agen (`render_kkp_core`), jadi gate
    LKE dan penerapan overlay HITL (`TemuanReview.edited_fields`) tetap
    berlaku — koreksi manual auditor ikut ter-render, bukan versi agen.
    """
    user, role = current
    if role != Role.AT:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Render KKP hanya untuk Anggota Tim. Role Anda: {role.value}.",
        )
    p = await _get_penugasan_or_404(db, penugasan_id, current)

    from app.tools.kkp_tools import render_kkp_core

    ok, pesan = await render_kkp_core(p.folder_path, user.nama_lengkap or "")
    if not ok:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, pesan)
    nama_berkas = f"KKP-{(user.nama_lengkap or '').replace(' ', '-')}.docx"
    return {"ok": True, "file": nama_berkas, "detail": pesan}


@router.delete("/{penugasan_id}/temuan/{temuan_id}")
async def delete_temuan(
    penugasan_id: int,
    temuan_id: str,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Hapus 1 temuan dari _KKP/temuan.json + hapus TemuanReview row-nya. AT/KT/PT/PM."""
    user, role = current
    if role not in (Role.AT, Role.KT, Role.PT, Role.PM):
        raise HTTPException(status.HTTP_403_FORBIDDEN, f"Role {role.value} tidak bisa hapus temuan.")
    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    temuan_path = folder / "_KKP" / "temuan.json"
    if not temuan_path.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "temuan.json tidak ditemukan.")
    try:
        data = json.loads(temuan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Gagal baca temuan.json: {e}")
    temuan_list = data.get("temuan", []) if isinstance(data, dict) else []
    before = len(temuan_list)
    data["temuan"] = [t for t in temuan_list if str(t.get("id_temuan") or "").strip() != temuan_id]
    if len(data["temuan"]) == before:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Temuan {temuan_id} tidak ditemukan.")
    temuan_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    rev = (await db.execute(
        select(TemuanReview).where(
            TemuanReview.penugasan_id == penugasan_id,
            TemuanReview.temuan_id == temuan_id,
        )
    )).scalar_one_or_none()
    if rev:
        await db.delete(rev)
        await db.commit()

    return {"ok": True, "deleted": temuan_id, "total_remaining": len(data["temuan"])}


async def _upsert_review(
    db: AsyncSession,
    penugasan_id: int,
    temuan_id: str,
    status_new: str,
    note: str | None,
    user_id: int,
) -> dict[str, Any]:
    """Upsert TemuanReview row + commit."""
    existing = (
        await db.execute(
            select(TemuanReview).where(
                TemuanReview.penugasan_id == penugasan_id,
                TemuanReview.temuan_id == temuan_id,
            )
        )
    ).scalar_one_or_none()
    if existing:
        existing.status = status_new
        existing.note = note
        existing.reviewed_by_user_id = user_id
        existing.reviewed_at = datetime.utcnow()
    else:
        existing = TemuanReview(
            penugasan_id=penugasan_id,
            temuan_id=temuan_id,
            status=status_new,
            note=note,
            reviewed_by_user_id=user_id,
            reviewed_at=datetime.utcnow(),
        )
        db.add(existing)
    await db.commit()
    return {
        "ok": True,
        "id_temuan": temuan_id,
        "status": status_new,
        "reviewed_at": existing.reviewed_at.isoformat() + "Z" if existing.reviewed_at else None,
    }


# ============================================================
# Reviu Konsep LHP (tahapan 6 — LRS LHP) — PT/PM menyetujui / minta revisi
# ============================================================


class LhpReviewCreate(BaseModel):
    status: Literal["APPROVED", "NEEDS_REVISION"]
    catatan: str | None = None


def _lhp_review_dict(r: LhpReview, reviewer_name: str | None = None) -> dict[str, Any]:
    return {
        "id": r.id,
        "status": r.status,
        "catatan": r.catatan,
        "reviewer_user_id": r.reviewer_user_id,
        "reviewer_role": r.reviewer_role,
        "reviewer_name": reviewer_name,
        "reviewed_at": r.reviewed_at.isoformat() + "Z" if r.reviewed_at else None,
    }


@router.get("/{penugasan_id}/lhp-review")
async def list_lhp_review(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Riwayat reviu konsep LHP (semua role bisa baca). Terbaru di atas.

    `latest_status` ringkasan untuk derive tahapan 6 di UI:
      APPROVED → tahapan selesai; NEEDS_REVISION → revisi diminta; null → belum direviu.
    """
    await _get_penugasan_or_404(db, penugasan_id, current)
    rows = (
        await db.execute(
            select(LhpReview)
            .where(LhpReview.penugasan_id == penugasan_id)
            .order_by(LhpReview.reviewed_at.desc(), LhpReview.id.desc())
        )
    ).scalars().all()

    # Nama reviewer (best-effort — map user_id → nama_lengkap)
    user_ids = {r.reviewer_user_id for r in rows if r.reviewer_user_id}
    names: dict[int, str] = {}
    if user_ids:
        users = (
            await db.execute(select(User).where(User.id.in_(user_ids)))
        ).scalars().all()
        names = {u.id: u.nama_lengkap for u in users}

    items = [_lhp_review_dict(r, names.get(r.reviewer_user_id or -1)) for r in rows]
    return {
        "total": len(items),
        "latest_status": items[0]["status"] if items else None,
        "items": items,
    }


@router.post("/{penugasan_id}/lhp-review", status_code=status.HTTP_201_CREATED)
async def create_lhp_review(
    penugasan_id: int,
    payload: LhpReviewCreate,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Reviu konsep LHP — hanya Pengendali Teknis (PT) / Pengendali Mutu (PM).

    Setiap aksi disimpan sebagai baris baru (history). UI memakai baris terbaru
    untuk menentukan status tahapan 6 (LRS LHP).
    """
    user, role = current
    if role not in (Role.PT, Role.PM):
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            f"Reviu konsep LHP hanya untuk Pengendali Teknis/Mutu (PT/PM). Role Anda: {role.value}.",
        )
    if payload.status == "NEEDS_REVISION" and not (payload.catatan or "").strip():
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "Catatan revisi wajib diisi saat meminta revisi.",
        )
    penugasan = await _get_penugasan_or_404(db, penugasan_id, current)

    review = LhpReview(
        penugasan_id=penugasan_id,
        reviewer_user_id=user.id,
        reviewer_role=role.value,
        status=payload.status,
        catatan=(payload.catatan or None),
    )
    db.add(review)
    await db.commit()
    await db.refresh(review)

    # C5 — tutup lingkaran: LHP disetujui (laporan terbit) → tarik rekomendasi ke TLHP.
    tlhp_ditambahkan = 0
    daftar_temuan_path: str | None = None
    if payload.status == "APPROVED":
        try:
            from app.routes.tlhp import ingest_tlhp_from_penugasan
            tlhp_ditambahkan = await ingest_tlhp_from_penugasan(db, penugasan)
        except Exception:  # noqa: BLE001 — best-effort, jangan gagalkan approval
            import logging
            logging.getLogger(__name__).exception("Auto-ingest TLHP gagal untuk penugasan %s", penugasan_id)
        # Fase 3 — garis serah: hasilkan Daftar Temuan & Rekomendasi (paket ekspor ke administrasi/TU).
        try:
            from pathlib import Path
            from app.export_dhp import build_daftar_temuan_rekomendasi
            _p = build_daftar_temuan_rekomendasi(Path(penugasan.folder_path))
            daftar_temuan_path = str(_p) if _p else None
        except Exception:  # noqa: BLE001 — best-effort
            import logging
            logging.getLogger(__name__).exception("Generate Daftar Temuan gagal utk penugasan %s", penugasan_id)

    return {
        "ok": True,
        "tlhp_ditambahkan": tlhp_ditambahkan,
        "daftar_temuan_path": daftar_temuan_path,
        **_lhp_review_dict(review, user.nama_lengkap),
    }


# ─── Survei Pendahuluan (port dari v8.8 SIMWAS) ───────────────────────────
def _newest_doc_mtime(folder: Path) -> float:
    """mtime dokumen sumber + digest terbaru (penanda 'ada file baru').

    Cek folder input dokumen + `_INGESTED/` (hasil ingest). Return 0.0 bila kosong.
    """
    newest = 0.0
    scan_dirs = ["00-input", "00-survey", "01-peraturan-internal", "02-kontrak",
                 "03-perencanaan", "04-pelaksanaan", "05-keuangan", "_INGESTED"]
    for sub in scan_dirs:
        d = folder / sub
        if not d.is_dir():
            continue
        for f in d.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                try:
                    newest = max(newest, f.stat().st_mtime)
                except OSError:
                    pass
    return newest


@router.get("/{penugasan_id}/context-survey-status")
async def get_context_survey_status(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Status konteks & survei untuk tombol 3-state di UI.

    - is_audit       : skill termasuk skill audit (punya survei pendahuluan)?
    - context_exists : context.md sudah ada?
    - survey_exists  : _SURVEY/Survei-Pendahuluan.docx sudah ada?
    - stale          : ada dokumen yang LEBIH BARU dari output (perlu generate ulang)?
    """
    from app.survey_pendahuluan import is_audit_skill

    p = await _get_penugasan_or_404(db, penugasan_id, current)
    folder = Path(p.folder_path)
    is_audit = is_audit_skill(p.skill)
    ctx_path = folder / "context.md"
    survey_path = folder / "_SURVEY" / "Survei-Pendahuluan.docx"
    context_exists = ctx_path.exists()
    survey_exists = survey_path.exists()

    newest_doc = _newest_doc_mtime(folder)
    # Output mtime terkecil yang relevan: bila salah satu belum ada → 0 (pasti stale).
    out_mtimes = []
    if context_exists:
        out_mtimes.append(ctx_path.stat().st_mtime)
    if is_audit:
        out_mtimes.append(survey_path.stat().st_mtime if survey_exists else 0.0)
    oldest_output = min(out_mtimes) if out_mtimes else 0.0

    if is_audit:
        generated = context_exists and survey_exists
    else:
        generated = context_exists
    stale = generated and newest_doc > oldest_output

    return {
        "is_audit": is_audit,
        "context_exists": context_exists,
        "survey_exists": survey_exists,
        "generated": generated,
        "stale": stale,
    }


@router.post("/{penugasan_id}/survey-pendahuluan")
async def render_survey_pendahuluan_route(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """Render Laporan Survei Pendahuluan (.docx). HANYA skill audit.

    Dipanggil frontend SETELAH context.md selesai digenerate agen, agar isi
    survei (Gambaran Umum dll) ikut yang terbaru.
    """
    from app.survey_pendahuluan import is_audit_skill, render_survey_pendahuluan

    p = await _get_penugasan_or_404(db, penugasan_id, current)
    if not is_audit_skill(p.skill):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Survei pendahuluan hanya untuk skill audit (skill saat ini: {p.skill}).",
        )
    folder = Path(p.folder_path)
    if not (folder / "context.md").exists():
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            "context.md belum ada — generate konteks dulu sebelum survei pendahuluan.",
        )
    out_path = render_survey_pendahuluan(folder, skill=p.skill, obyek=p.obyek)
    return {
        "ok": True,
        "path": str(out_path.relative_to(folder)),
        "name": out_path.name,
    }

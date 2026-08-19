"""Routes TLHP — Tindak Lanjut Hasil Pengawasan (Workstream C5, pilar ke-4).

Memantau status rekomendasi LHP/LHR sampai tuntas — menutup lingkaran pengawasan.
Sumber data DB (`tlhp_rekomendasi`):
- seed dummy dari fixture `tlhp-dummy.json` (saat tabel kosong);
- AUTO-INGEST dari `_LHP/rekomendasi.json` saat konsep LHP disetujui PT/PM
  (`ingest_tlhp_from_penugasan`) → laporan terbit langsung jadi item TLHP.

Aging (warna): 0–90 HIJAU · 91–180 KUNING · 181–365 ORANGE · >365 MERAH.
Kritis = umur >365 hari DAN status belum SUDAH.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.database import get_db
from app.models import Penugasan, Role, TlhpRekomendasi, User
from app.tenancy import assert_akses_penugasan

router = APIRouter(prefix="/tlhp", tags=["tlhp"])

_FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "tlhp-dummy.json"


def _aging(umur: int) -> str:
    if umur <= 90:
        return "HIJAU"
    if umur <= 180:
        return "KUNING"
    if umur <= 365:
        return "ORANGE"
    return "MERAH"


def _enrich(r: TlhpRekomendasi) -> dict:
    umur = warna = None
    if r.tgl_lhp:
        try:
            tgl = datetime.strptime(r.tgl_lhp, "%Y-%m-%d").date()
            umur = (datetime.utcnow().date() - tgl).days
            warna = _aging(umur)
        except Exception:  # noqa: BLE001
            pass
    selesai = (r.status or "").upper() == "SUDAH"
    return {
        "no_rek": r.no_rek, "penugasan_id": r.penugasan_id, "asal_lhp": r.asal_lhp,
        "satker": r.satker, "satker_kode": r.satker_kode, "substansi": r.substansi,
        "pic": r.pic, "tgl_lhp": r.tgl_lhp, "deadline": r.deadline, "status": r.status,
        "bukti_tl": r.bukti_tl, "sumber": r.sumber,
        "umur_hari": umur, "warna": warna,
        "kritis": bool(umur is not None and umur > 365 and not selesai),
    }


async def _all(db: AsyncSession) -> list[TlhpRekomendasi]:
    return list((await db.execute(select(TlhpRekomendasi).order_by(TlhpRekomendasi.tgl_lhp.desc()))).scalars())


async def tlhp_summary(db: AsyncSession) -> dict:
    """Ringkasan untuk dashboard F4 (dipanggil juga oleh routes/dashboard.py)."""
    items = [_enrich(r) for r in await _all(db)]
    total = len(items)
    by_status: dict[str, int] = {}
    by_warna: dict[str, int] = {}
    for it in items:
        by_status[it["status"]] = by_status.get(it["status"], 0) + 1
        w = it["warna"] or "-"
        by_warna[w] = by_warna.get(w, 0) + 1
    selesai = by_status.get("SUDAH", 0)
    kritis = sorted([i for i in items if i["kritis"]], key=lambda x: x["umur_hari"] or 0, reverse=True)
    return {
        "tersedia": True, "total": total, "selesai": selesai,
        "proses": by_status.get("PROSES", 0), "belum": by_status.get("BELUM", 0),
        "tidak_dapat": by_status.get("TIDAK_DAPAT", 0),
        "persen_selesai": round(selesai / total * 100, 1) if total else 0.0,
        "by_warna": by_warna, "kritis_count": len(kritis),
        "kritis": [{"no_rek": k["no_rek"], "satker": k["satker"], "substansi": (k["substansi"] or "")[:90],
                    "umur_hari": k["umur_hari"], "pic": k["pic"]} for k in kritis[:5]],
    }


async def seed_tlhp_dummy(db: AsyncSession) -> int:
    """Seed dummy ke DB bila tabel kosong (idempoten). Dipanggil saat startup."""
    n = (await db.execute(select(func.count()).select_from(TlhpRekomendasi))).scalar() or 0
    if n > 0:
        return 0
    try:
        data = json.loads(_FIXTURE.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return 0
    added = 0
    for r in data.get("rekomendasi", []):
        db.add(TlhpRekomendasi(
            no_rek=r.get("no_rek"), asal_lhp=r.get("asal_lhp", ""), satker=r.get("satker", ""),
            satker_kode=r.get("satker_kode"), substansi=r.get("substansi", ""), pic=r.get("pic"),
            tgl_lhp=r.get("tgl_lhp"), deadline=r.get("deadline"), status=r.get("status", "BELUM"),
            bukti_tl=r.get("bukti_tl"), sumber="dummy",
        ))
        added += 1
    await db.commit()
    return added


async def ingest_tlhp_from_penugasan(db: AsyncSession, penugasan: Penugasan) -> int:
    """Buat item TLHP dari rekomendasi LHP penugasan (menutup lingkaran).

    Baca `_LHP/rekomendasi.json` ({id_temuan: teks}) + `_KKP/temuan.json` (konteks).
    Anti-duplikat via `no_rek = REK-{penugasan.id}-{id_temuan}`.
    """
    folder = Path(penugasan.folder_path)
    rek_path = folder / "_LHP" / "rekomendasi.json"
    if not rek_path.exists():
        return 0
    try:
        rekomendasi = json.loads(rek_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return 0
    if not isinstance(rekomendasi, dict) or not rekomendasi:
        return 0

    today = datetime.utcnow().date()
    deadline = (today + timedelta(days=60)).isoformat()
    skill = penugasan.skill if isinstance(penugasan.skill, str) else getattr(penugasan.skill, "value", "")
    asal = f"LHP {skill} — {penugasan.obyek}"[:300]
    added = 0
    for tid, teks in rekomendasi.items():
        if not str(teks or "").strip():
            continue
        no_rek = f"REK-{penugasan.id}-{tid}"
        exists = (await db.execute(
            select(TlhpRekomendasi.id).where(TlhpRekomendasi.no_rek == no_rek)
        )).first()
        if exists:
            continue
        db.add(TlhpRekomendasi(
            no_rek=no_rek, penugasan_id=penugasan.id, temuan_id=tid,
            asal_lhp=asal, satker=penugasan.obyek[:200], substansi=str(teks),
            pic=None, tgl_lhp=today.isoformat(), deadline=deadline,
            status="BELUM", sumber="ingest",
        ))
        added += 1
    if added:
        await db.commit()
    return added


# --------------------------------------------------------------------------- #

@router.get("")
async def list_tlhp(
    _current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    satker_kode: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
) -> dict:
    """Daftar rekomendasi TLHP (ber-aging). Filter opsional: satker_kode, status."""
    items = [_enrich(r) for r in await _all(db)]
    if satker_kode:
        items = [i for i in items if i["satker_kode"] == satker_kode]
    if status_filter:
        items = [i for i in items if (i["status"] or "").upper() == status_filter.upper()]
    return {"total": len(items), "items": items}


@router.get("/summary")
async def get_tlhp_summary(
    _current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await tlhp_summary(db)


@router.post("/ingest/{penugasan_id}")
async def ingest_tlhp(
    penugasan_id: int,
    current: tuple[User, Role] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Tarik rekomendasi LHP penugasan ke TLHP (manual; auto juga saat LHP disetujui PT/PM)."""
    user, role = current
    if role not in (Role.KT, Role.PT, Role.PM):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Hanya KT/PT/PM yang dapat menarik rekomendasi ke TLHP.")
    p = (await db.execute(select(Penugasan).where(Penugasan.id == penugasan_id))).scalar_one_or_none()
    assert_akses_penugasan(p, user)  # ISOLASI Inspektorat
    n = await ingest_tlhp_from_penugasan(db, p)
    return {"ok": True, "ditambahkan": n,
            "pesan": f"{n} rekomendasi ditarik ke TLHP." if n else "Tidak ada rekomendasi baru (atau _LHP/rekomendasi.json belum ada)."}

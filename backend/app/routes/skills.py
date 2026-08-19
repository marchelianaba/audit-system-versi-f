"""Routes Skill — daftar skill pengawasan terdaftar (folder-driven).

Dipakai frontend untuk dropdown jenis penugasan (dinamis, bukan hardcode).
Read-only; sumber data = app.skills_registry (path APP_SKILLS_PATH).
"""
from fastapi import APIRouter, Depends

from app.auth import get_current_user
from app.models import Role, User
from app.skills_registry import list_skills

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
async def get_skills(
    _current: tuple[User, Role] = Depends(get_current_user),
) -> list[dict]:
    """Daftar skill terdaftar (slug, name, jenis, output, has_pipeline)."""
    return [
        {
            "slug": s["slug"],
            "name": s["name"],
            "jenis": s["jenis"],
            "output": s["output"],
            "has_pipeline": s["has_pipeline"],
        }
        for s in list_skills()
    ]


# ===========================================================================
# Baca skill — SKILL.md + berkas referensi. HANYA BACA.
#
# Turunan FREE: endpoint tulis (PUT /skills/{slug} & POST /skills) DICABUT.
# Skill di FREE dipatok allowlist 7 buah dan diperbarui lewat pengembang
# (commit ke repo), bukan lewat API — supaya isi skill yang menentukan
# perilaku agen tidak bisa diubah dari sisi pengguna.
# ===========================================================================
import re
from pathlib import Path

from fastapi import HTTPException, status

from app.skills_registry import (
    get_skill_md,
    list_skill_references,
    skill_dir,
)

_SLUG_RE = r"^[a-z0-9]+(-[a-z0-9]+)*$"
_REF_NAME_RE = r"^[A-Za-z0-9._\-]+$"


@router.get("/{slug}")
async def get_skill_detail(
    slug: str,
    _current: tuple[User, Role] = Depends(get_current_user),
) -> dict:
    """Detail 1 skill: isi SKILL.md + daftar reference. Semua role baca."""
    if not re.match(_SLUG_RE, slug):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Slug tidak valid.")
    content = get_skill_md(slug)
    if content is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Skill '{slug}' tidak ada.")
    return {
        "slug": slug,
        "content": content,
        "references": list_skill_references(slug),
    }


@router.get("/{slug}/reference")
async def get_skill_reference(
    slug: str,
    path: str,
    _current: tuple[User, Role] = Depends(get_current_user),
) -> dict:
    """Baca isi 1 file reference skill (read-only, hanya file teks)."""
    if not re.match(_SLUG_RE, slug):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Slug tidak valid.")
    d = skill_dir(slug)
    if d is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Skill '{slug}' tidak ada.")
    # Anti path-traversal: path harus persis salah satu dari list_skill_references.
    if path not in list_skill_references(slug):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Reference '{path}' tidak terdaftar di skill ini.")
    f = d / path
    if f.suffix.lower() in (".pdf", ".docx", ".xlsx", ".png", ".jpg"):
        return {"slug": slug, "path": path, "binary": True,
                "content": f"(file biner {f.suffix} — {f.stat().st_size:,} bytes; buka dari folder skill)"}
    try:
        return {"slug": slug, "path": path, "binary": False,
                "content": f.read_text(encoding="utf-8")[:120_000]}
    except (OSError, UnicodeDecodeError) as e:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Gagal baca: {e}")

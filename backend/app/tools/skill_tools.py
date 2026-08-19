"""Tools skill — agen memuat prosedur skill pengawasan saat runtime.

v7 awalnya hanya tahu alur reviu-rka-kl / reviu-pengadaan (lewat prompts). Untuk
skill pengawasan lain (audit-kinerja, evaluasi-sakip, dll), agen TIDAK punya alur
hardcoded — ia memuat `SKILL.md` + references lewat tools di sini, lalu mengikuti
gate/workflow yang tertulis di skill tersebut.

Sumber data: registry folder-driven (app.skills_registry, path APP_SKILLS_PATH).
Semua baca read-only + path-traversal safe + di-cap supaya context tak meledak.
"""
import json

from claude_agent_sdk import tool

from app import skills_registry as reg

_SKILL_MD_CAP = 14000
_REF_CAP = 14000


@tool(
    "list_available_skills",
    "Daftar skill pengawasan yang terdaftar di sistem (folder-driven). "
    "Return {slug, name, jenis, output, has_pipeline}. Pakai untuk tahu skill apa "
    "yang didukung. Untuk memuat prosedur sebuah skill, panggil `load_skill(skill)`.",
    {},
)
async def list_available_skills(_args: dict) -> dict:
    skills = [
        {
            "slug": s["slug"],
            "name": s["name"],
            "jenis": s["jenis"],
            "output": s["output"],
            "has_pipeline": s["has_pipeline"],
        }
        for s in reg.list_skills()
    ]
    return {
        "content": [{
            "type": "text",
            "text": json.dumps({"total": len(skills), "skills": skills}, ensure_ascii=False),
        }]
    }


@tool(
    "load_skill",
    "Muat prosedur sebuah skill pengawasan: isi SKILL.md (definisi, gate/workflow, "
    "format temuan) + daftar references yang tersedia. WAJIB dipanggil di awal bila "
    "skill penugasan BUKAN reviu-rka-kl/reviu-pengadaan, lalu IKUTI langkah di "
    "SKILL.md. Baca isi reference via `read_skill_reference(skill, reference)`.",
    {"skill": str},
)
async def load_skill(args: dict) -> dict:
    skill = str(args.get("skill", "")).strip()
    md = reg.get_skill_md(skill)
    if md is None:
        return {
            "content": [{
                "type": "text",
                "text": (
                    f"NOT_FOUND|skill='{skill}' tidak punya SKILL.md. "
                    f"Tersedia: {', '.join(reg.available_slugs())}"
                ),
            }],
            "is_error": True,
        }
    refs = reg.list_skill_references(skill)
    payload = {
        "skill": reg._slugify(skill),
        "references": refs,
        "truncated": len(md) > _SKILL_MD_CAP,
        "skill_md": md[:_SKILL_MD_CAP],
    }
    return {"content": [{"type": "text", "text": json.dumps(payload, ensure_ascii=False)}]}


@tool(
    "read_skill_reference",
    "Baca isi satu file reference milik skill (mis. checklist, panduan ekstraksi "
    "kriteria, bahasa keyakinan). `reference` = path relatif dari `load_skill` "
    "(mis. 'references/08-checklist-survey-pendahuluan.md'). Read-only, di-cap.",
    {"skill": str, "reference": str},
)
async def read_skill_reference(args: dict) -> dict:
    skill = str(args.get("skill", "")).strip()
    reference = str(args.get("reference", "")).strip()
    text = reg.read_skill_reference(skill, reference)
    if text is None:
        return {
            "content": [{
                "type": "text",
                "text": (
                    f"NOT_FOUND|reference='{reference}' tidak ada di skill '{skill}'. "
                    f"Cek daftar lewat load_skill('{skill}')."
                ),
            }],
            "is_error": True,
        }
    truncated = len(text) > _REF_CAP
    head = f"[reference={reference} skill={skill}{' · truncated' if truncated else ''}]\n\n"
    return {"content": [{"type": "text", "text": head + text[:_REF_CAP]}]}


SKILL_TOOLS = [list_available_skills, load_skill, read_skill_reference]

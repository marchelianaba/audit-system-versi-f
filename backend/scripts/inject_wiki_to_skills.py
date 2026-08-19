#!/usr/bin/env python3
"""Injeksi isi wiki → skill sebagai SNAPSHOT BEKU (untuk turunan FREE).

LATAR
-----
Turunan FREE tidak membawa wiki sebagai fitur (tanpa `search_wiki`,
`list_temuan_patterns`, menu Knowledge, Chat, tulis-balik). Supaya FREE tetap
berfungsi, ISI wiki dipindahkan ke dalam skill sebagai berkas `references/`.
Setelah itu isinya BEKU: tidak ikut berubah ketika wiki di FULL diperbarui.

Ini bekerja tanpa tool baru karena `skills_registry.list_skill_references()`
memindai `references/` secara REKURSIF — berkas hasil injeksi otomatis terlihat
agen lewat `read_skill_reference`.

PETA INJEKSI
------------
  wiki/temuan-patterns/<skill>/      -> skills/<skill>/references/90-pattern-temuan/
  wiki/konteks/*.md + regulasi/      -> skills/<TIAP skill>/references/90-konteks-organisasi/
  wiki/templates/kp/kp-<skill>.md    -> skills/<skill>/references/91-template-kp.md
  wiki/templates/pkp/pkp-<skill>.md  -> skills/<skill>/references/92-template-pkp.md

PEMAKAIAN
---------
  python scripts/inject_wiki_to_skills.py            # pratinjau (tidak menulis)
  python scripts/inject_wiki_to_skills.py --apply    # jalankan injeksi
  python scripts/inject_wiki_to_skills.py --revert   # bersihkan hasil injeksi

Idempoten: `--apply` boleh dijalankan berulang (menyegarkan snapshot).
Jejak apa saja yang ditulis disimpan di manifest agar `--revert` bersih total.
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]        # akar repo
WIKI = ROOT / "knowledge" / "wiki"
SKILLS = ROOT / "knowledge" / "skills"
MANIFEST = SKILLS / ".wiki-injection-manifest.json"

DIR_PATTERN = "90-pattern-temuan"
DIR_KONTEKS = "90-konteks-organisasi"
FILE_KP = "91-template-kp.md"
FILE_PKP = "92-template-pkp.md"

_BANNER = (
    "<!-- ============================================================\n"
    "     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)\n"
    "     Sumber  : {src}\n"
    "     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:\n"
    "       python scripts/inject_wiki_to_skills.py --apply\n"
    "     ============================================================ -->\n\n"
)


def _skill_ada(nama: str) -> bool:
    return (SKILLS / nama / "SKILL.md").is_file()


def _tulis(dst: Path, src: Path, ditulis: list[str], apply: bool) -> None:
    """Salin `src` → `dst` dengan banner asal-usul."""
    rel_src = src.relative_to(ROOT)
    if apply:
        dst.parent.mkdir(parents=True, exist_ok=True)
        isi = src.read_text(encoding="utf-8", errors="replace")
        dst.write_text(_BANNER.format(src=rel_src) + isi, encoding="utf-8")
    ditulis.append(str(dst.relative_to(ROOT)))


def injeksi(apply: bool) -> dict:
    if not WIKI.is_dir():
        print(f"FATAL: folder wiki tidak ditemukan: {WIKI}")
        sys.exit(1)

    ditulis: list[str] = []
    lewat: list[str] = []
    n_pattern = n_tpl = n_konteks = 0

    # --- 1) pattern temuan per skill ---
    src_pat = WIKI / "temuan-patterns"
    for folder in sorted(p for p in src_pat.iterdir() if p.is_dir()) if src_pat.is_dir() else []:
        skill = folder.name
        if not _skill_ada(skill):
            lewat.append(f"pattern '{skill}' — tidak ada di knowledge/skills/ "
                         f"(bukan skill terdaftar; tak terjangkau read_skill_reference)")
            continue
        for f in sorted(folder.rglob("*.md")):
            _tulis(SKILLS / skill / "references" / DIR_PATTERN / f.relative_to(folder),
                   f, ditulis, apply)
            n_pattern += 1

    # --- 2) konteks lintas-skill → DISALIN KE TIAP SKILL TERDAFTAR ---
    # Catatan (hasil uji): folder penampung bersama seperti `panduan-format-umum`
    # TIDAK terjangkau agen — registry hanya mendaftar folder ber-`SKILL.md`,
    # sehingga `read_skill_reference('panduan-format-umum', …)` mengembalikan None.
    # Maka konteks digandakan ke references tiap skill. Ukurannya kecil (beberapa
    # KB per skill) dan ini snapshot beku, jadi duplikasi tidak menimbulkan drift.
    src_ktx = WIKI / "konteks"
    if src_ktx.is_dir():
        skill_terdaftar = sorted(d.name for d in SKILLS.iterdir() if _skill_ada(d.name))
        berkas_ktx = sorted(src_ktx.rglob("*.md"))
        for skill in skill_terdaftar:
            for f in berkas_ktx:
                _tulis(SKILLS / skill / "references" / DIR_KONTEKS / f.relative_to(src_ktx),
                       f, ditulis, apply)
                n_konteks += 1

    # --- 3) template KP/PKP per skill ---
    for kind, nama_berkas in (("kp", FILE_KP), ("pkp", FILE_PKP)):
        src_tpl = WIKI / "templates" / kind
        if not src_tpl.is_dir():
            continue
        for f in sorted(src_tpl.glob(f"{kind}-*.md")):
            skill = f.stem[len(kind) + 1:]          # "kp-audit-umum" -> "audit-umum"
            if skill == "default" or not _skill_ada(skill):
                if skill != "default":
                    lewat.append(f"template {kind} '{skill}' — skill tidak ada")
                continue
            _tulis(SKILLS / skill / "references" / nama_berkas, f, ditulis, apply)
            n_tpl += 1

    ringkas = {
        "dibekukan_pada": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "n_pattern": n_pattern, "n_konteks": n_konteks, "n_template": n_tpl,
        "total_berkas": len(ditulis), "berkas": sorted(ditulis), "dilewati": lewat,
    }
    if apply:
        MANIFEST.write_text(json.dumps(ringkas, ensure_ascii=False, indent=2), encoding="utf-8")
    return ringkas


def revert() -> None:
    if not MANIFEST.is_file():
        print("Tidak ada manifest — belum pernah injeksi (atau sudah di-revert).")
        return
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    n = 0
    for rel in data.get("berkas", []):
        p = ROOT / rel
        if p.is_file():
            p.unlink()
            n += 1
    # bersihkan folder injeksi yang kosong
    for skill_dir in SKILLS.iterdir():
        for d in (DIR_PATTERN, DIR_KONTEKS):
            folder = skill_dir / "references" / d
            if folder.is_dir():
                shutil.rmtree(folder, ignore_errors=True)
    MANIFEST.unlink()
    print(f"✓ Revert selesai — {n} berkas hasil injeksi dihapus, manifest dibuang.")


def main() -> None:
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--revert":
        revert()
        return
    apply = arg == "--apply"
    r = injeksi(apply)

    judul = "INJEKSI DIJALANKAN" if apply else "PRATINJAU (tidak ada berkas ditulis)"
    print(f"=== {judul} ===")
    print(f"  pattern temuan : {r['n_pattern']:>4} berkas")
    print(f"  konteks wiki   : {r['n_konteks']:>4} berkas  → tiap skill/references/{DIR_KONTEKS}/")
    print(f"  template KP/PKP: {r['n_template']:>4} berkas")
    print(f"  TOTAL          : {r['total_berkas']:>4} berkas")
    if r["dilewati"]:
        print("\n  DILEWATI:")
        for x in r["dilewati"]:
            print(f"    - {x}")
    if not apply:
        print("\n  Jalankan dengan --apply untuk menulis; --revert untuk membersihkan.")


if __name__ == "__main__":
    main()

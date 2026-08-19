"""Penentuan skill dari Jenis + Sub Penugasan, dibantu tebakan dari judul.

LATAR. Sebelumnya Pengendali Teknis memilih skill sendiri dari sebuah daftar —
menuntut hafal skill mana yang cocok untuk penugasan apa, dan sekali salah tak
bisa diperbaiki (tak ada jalur mengubah skill sama sekali).

Sekarang skill DITURUNKAN dari dua isian yang memang sudah menjadi identitas
penugasan di SIMWAS: **Jenis Penugasan** (audit/reviu/evaluasi/pemantauan) dan
**Sub Penugasan** (RKA-K/L, pengadaan, lainnya). Judul penugasan hanya dipakai
untuk MENEBAK isian awal keduanya — tebakan itu tinggal dibenarkan, dan tidak
pernah menjadi penentu akhir. Menebak dari judul saja terlalu rapuh: judul
seperti "Reviu Pengadaan pada Penyusunan RKA-K/L" memuat dua kata kunci
sekaligus, dan tebakan yang salah akan mengunci penugasan ke skill keliru.

Kombinasi yang tak punya skill khusus jatuh ke `*-umum` sesuai jenisnya —
ketajamannya lalu datang dari kriteria yang wajib disediakan auditor.
"""
from __future__ import annotations

import re

JENIS_PILIHAN = ["Audit", "Reviu", "Evaluasi", "Pemantauan"]

SUB_RKA = "RKA-K/L"
SUB_PBJ = "Pengadaan Barang/Jasa"
SUB_LAIN = "Lainnya"
SUB_PILIHAN = [SUB_RKA, SUB_PBJ, SUB_LAIN]

# Matriks penentu skill. Hanya Reviu yang punya skill berdomain khusus; jenis
# lain jatuh ke *-umum karena skill spesialistisnya (audit-pengadaan,
# audit-kinerja, pemantauan-pengadaan, dst) tidak aktif di FREE.
_MATRIKS = {
    ("Reviu", SUB_RKA): "reviu-rka-kl",
    ("Reviu", SUB_PBJ): "reviu-pengadaan",
    ("Reviu", SUB_LAIN): "reviu-umum",
    ("Audit", SUB_RKA): "audit-umum",
    ("Audit", SUB_PBJ): "audit-umum",
    ("Audit", SUB_LAIN): "audit-umum",
    ("Evaluasi", SUB_RKA): "evaluasi-umum",
    ("Evaluasi", SUB_PBJ): "evaluasi-umum",
    ("Evaluasi", SUB_LAIN): "evaluasi-umum",
    ("Pemantauan", SUB_RKA): "pemantauan-umum",
    ("Pemantauan", SUB_PBJ): "pemantauan-umum",
    ("Pemantauan", SUB_LAIN): "pemantauan-umum",
}

# Kata kunci penebak. Dicocokkan sebagai KATA UTUH — pola `(?<![a-z])x(?![a-z])`
# sama dengan yang dipakai `storage._token`. Tanpa itu, "audit" ikut menyala
# pada kata "auditor" (kelas kesalahan yang pernah nyata terjadi di repo ini
# ketika "tor" cocok dengan "audiTOR").
_KATA_JENIS: list[tuple[str, tuple[str, ...]]] = [
    ("Reviu", ("reviu", "review")),
    ("Audit", ("audit", "pemeriksaan")),
    ("Evaluasi", ("evaluasi",)),
    ("Pemantauan", ("pemantauan", "monitoring", "tindak lanjut")),
]

_KATA_SUB: list[tuple[str, tuple[str, ...]]] = [
    (SUB_RKA, ("rka-k/l", "rka-kl", "rkakl", "rka", "pagu anggaran", "rencana kerja dan anggaran")),
    (SUB_PBJ, ("pengadaan", "pbj", "barang/jasa", "barang dan jasa", "tender", "kontrak", "hps")),
]


def _posisi(teks: str, kata: str) -> int:
    """Posisi kemunculan pertama kata (-1 bila tak ada). Kata pendek dicocokkan
    sebagai KATA UTUH supaya "audit" tak menyala pada "auditor"."""
    if " " in kata or "/" in kata or "-" in kata:
        return teks.find(kata)
    m = re.search(rf"(?<![a-z]){re.escape(kata)}(?![a-z])", teks)
    return m.start() if m else -1


def _ada(teks: str, kata: str) -> bool:
    return _posisi(teks, kata) >= 0


def tebak_dari_judul(judul: str | None) -> dict:
    """Tebak Jenis & Sub dari judul penugasan. Hanya ISIAN AWAL, bukan penentu.

    Ambigu (judul memuat kata kunci dua Sub sekaligus) → Sub dikosongkan dengan
    alasan yang terbaca. Lebih baik diam daripada salah mengunci.
    """
    t = (judul or "").strip().lower()
    if not t:
        return {"jenis": None, "sub": None, "alasan": "", "ambigu": False}

    # Jenis ditentukan oleh kata kunci yang muncul PALING AWAL, bukan urutan
    # daftar. Judul penugasan berbahasa Indonesia hampir selalu dibuka oleh
    # jenisnya ("Pemantauan Tindak Lanjut Hasil Pemeriksaan BPK") — memakai
    # urutan daftar membuat kata "pemeriksaan" di belakang mengalahkan
    # "Pemantauan" di depan.
    kandidat: list[tuple[int, str]] = []
    for j, kk in _KATA_JENIS:
        posisi = [_posisi(t, k) for k in kk]
        posisi = [x for x in posisi if x >= 0]
        if posisi:
            kandidat.append((min(posisi), j))
    jenis = min(kandidat)[1] if kandidat else None
    cocok_sub = [s for s, kk in _KATA_SUB if any(_ada(t, k) for k in kk)]

    alasan_bagian: list[str] = []
    ambigu = False
    if jenis:
        alasan_bagian.append(f"kata '{jenis.lower()}' pada judul")

    if len(cocok_sub) > 1:
        ambigu = True
        sub = None
        alasan_bagian.append(
            "judul memuat kata kunci " + " dan ".join(cocok_sub) + " sekaligus — mohon pilih Sub"
        )
    elif cocok_sub:
        sub = cocok_sub[0]
        alasan_bagian.append(f"terdeteksi {sub}")
    else:
        sub = SUB_LAIN if jenis else None
        if jenis:
            alasan_bagian.append("tak ada kata kunci RKA-K/L maupun pengadaan → Lainnya")

    return {
        "jenis": jenis,
        "sub": sub,
        "ambigu": ambigu,
        "alasan": "; ".join(alasan_bagian),
    }


def skill_dari(jenis: str | None, sub: str | None) -> str | None:
    """Skill hasil matriks. None bila Jenis/Sub belum lengkap atau tak dikenal."""
    if not jenis or not sub:
        return None
    j = str(jenis).strip().title()
    s = str(sub).strip()
    # Toleransi penulisan Sub yang sedikit berbeda dari pilihan baku.
    for baku in SUB_PILIHAN:
        if s.lower() == baku.lower():
            s = baku
            break
    else:
        s = SUB_LAIN
    return _MATRIKS.get((j, s))


def jelaskan(jenis: str | None, sub: str | None) -> str:
    """Kalimat pendek: kenapa skill itu yang dipakai. Ditampilkan ke pengguna."""
    skill = skill_dari(jenis, sub)
    if not skill:
        return "Jenis dan Sub Penugasan belum lengkap."
    if skill.endswith("-umum"):
        return (
            f"{jenis} × {sub} → {skill}. Tidak ada skill khusus untuk kombinasi ini, "
            "jadi dipakai skill umum — kriterianya Anda sediakan sendiri di Tahapan 3."
        )
    return f"{jenis} × {sub} → {skill} (kriteria bakunya sudah melekat pada skill ini)."


def deteksi(judul: str | None) -> dict:
    """Satu panggilan untuk UI: tebakan Jenis/Sub + skill + alasannya."""
    t = tebak_dari_judul(judul)
    skill = skill_dari(t["jenis"], t["sub"])
    return {
        "jenis": t["jenis"],
        "sub": t["sub"],
        "ambigu": t["ambigu"],
        "skill": skill,
        "alasan": t["alasan"],
        "penjelasan": jelaskan(t["jenis"], t["sub"]) if skill else t["alasan"],
        "jenis_pilihan": JENIS_PILIHAN,
        "sub_pilihan": SUB_PILIHAN,
    }

"""Inisialisasi database: buat tabel + seed user uji.

Dipanggil saat first deploy (lihat fly.toml `release_command`) atau manual:
    python -m app.init_db
"""
import asyncio
import secrets

from sqlalchemy import select

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Role, User


# Password DEV akun seed (quick-login). Diambil dari env DEV_SEED_PASSWORD (.env,
# gitignored). Bila tak diset → password ACAK per-boot (dicetak ke log) agar TIDAK
# ada kredensial baked di repo (repo publik). PRODUKSI: jangan set + matikan quick-login.
_DEV_PW_FROM_ENV = (get_settings().dev_seed_password or "").strip()
DEV_PASSWORD = _DEV_PW_FROM_ENV or secrets.token_urlsafe(9)

# Inspektorat default untuk akun seed & backfill data lama (tim pemilik sistem).
DEFAULT_INSPEKTORAT = "II"

SEED_USERS = [
    # --- Inspektorat I, III, IV (dev seed) — untuk menguji & memakai isolasi.
    # Tiap Inspektorat butuh minimal PT (buat penugasan), KT (PKP), AT (analisis).
    *[
        {
            "username": f"pt{ins.lower()}",
            "email": f"pt.insp{ins.lower()}@komdigi.go.id",
            "nama_lengkap": f"Pengendali Teknis Inspektorat {ins}",
            "nip": f"1980010120100{n}1001",
            "role_default": Role.PT,
            "inspektorat": ins,
        } for n, ins in enumerate(("I", "III", "IV"), start=1)
    ],
    *[
        {
            "username": f"kt{ins.lower()}",
            "email": f"kt.insp{ins.lower()}@komdigi.go.id",
            "nama_lengkap": f"Ketua Tim Inspektorat {ins}",
            "nip": f"1980010120100{n}2001",
            "role_default": Role.KT,
            "inspektorat": ins,
        } for n, ins in enumerate(("I", "III", "IV"), start=1)
    ],
    *[
        {
            "username": f"at{ins.lower()}",
            "email": f"at.insp{ins.lower()}@komdigi.go.id",
            "nama_lengkap": f"Anggota Tim Inspektorat {ins}",
            "nip": f"1980010120100{n}3001",
            "role_default": Role.AT,
            "inspektorat": ins,
        } for n, ins in enumerate(("I", "III", "IV"), start=1)
    ],

    {
        "username": "sarah",
        "email": "auditor.at@komdigi.go.id",
        "nama_lengkap": "Sarah Aulia",
        "nip": "198501012010011001",
        "role_default": Role.AT,
    },
    {
        "username": "citra",
        "email": "auditor.at2@komdigi.go.id",
        "nama_lengkap": "Citra Lestari",
        "nip": "198803152012012002",
        "role_default": Role.AT,
    },
    {
        "username": "budi",
        "email": "auditor.kt@komdigi.go.id",
        "nama_lengkap": "Budi Hartono",
        "nip": "197505152005011002",
        "role_default": Role.KT,
    },
    {
        "username": "inspektur",
        "email": "inspektorat2.kominfo.2@gmail.com",
        "nama_lengkap": "Inspektorat II Komdigi",
        "nip": "197001012000011001",
        "role_default": Role.PT,
    },
    {
        "username": "doddy",
        "email": "pengendali.mutu@komdigi.go.id",
        "nama_lengkap": "Doddy Setiadi",
        "nip": "197203102000031001",
        "role_default": Role.PM,
    },
    {
        "username": "admin",
        "email": "admin@komdigi.go.id",
        "nama_lengkap": "Administrator",
        "nip": "100000000000000000",
        "role_default": Role.ADMIN,
    },
    {
        "username": "tu",
        "email": "tu@komdigi.go.id",
        "nama_lengkap": "Tata Usaha",
        "nip": "200000000000000000",
        "role_default": Role.TU,
    },
]


async def seed_auth(db) -> None:
    """Migrasi + seed username/password seed users (idempoten, dipanggil di startup).

    Tabel `users` lama (audit_v7) belum punya kolom username/password_hash → ALTER
    IF NOT EXISTS. Lalu isi username + bcrypt(DEV_PASSWORD) untuk akun seed yang kosong.
    """
    from sqlalchemy import text

    from app.auth import hash_password

    if not _DEV_PW_FROM_ENV:
        print(
            "[init_db] ⚠ DEV_SEED_PASSWORD belum di-set — memakai password seed ACAK "
            f"(berubah tiap boot, quick-login mati): {DEV_PASSWORD}"
        )

    # 1) Kolom (Postgres) — aman bila sudah ada.
    for ddl in (
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(80)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash VARCHAR(200)",
        # Role ADMIN (5 char) butuh kolom > VARCHAR(4) lama.
        "ALTER TABLE users ALTER COLUMN role_default TYPE VARCHAR(16)",
        "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)",
        # HITL KKP: log append-only edit manual temuan (akuntabilitas).
        "ALTER TABLE temuan_review ADD COLUMN IF NOT EXISTS edit_log JSONB",
        # ISOLASI Inspektorat I–IV (lihat app/tenancy.py).
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS inspektorat VARCHAR(4)",
        "ALTER TABLE penugasan ADD COLUMN IF NOT EXISTS inspektorat VARCHAR(4)",
        "CREATE INDEX IF NOT EXISTS ix_users_inspektorat ON users(inspektorat)",
        "CREATE INDEX IF NOT EXISTS ix_penugasan_inspektorat ON penugasan(inspektorat)",
        # Jenis & Sub Penugasan (identitas ala SIMWAS) — penentu skill.
        "ALTER TABLE penugasan ADD COLUMN IF NOT EXISTS jenis_penugasan VARCHAR(40)",
        "ALTER TABLE penugasan ADD COLUMN IF NOT EXISTS sub_penugasan VARCHAR(80)",
        "ALTER TABLE penugasan ADD COLUMN IF NOT EXISTS skill_override TEXT",
    ):
        try:
            await db.execute(text(ddl))
        except Exception:  # noqa: BLE001
            pass
    await db.commit()

    # 1b) BACKFILL isolasi — data yang dibuat SEBELUM fitur ini tidak punya
    # inspektorat. Dibiarkan NULL berarti tak seorang pun bisa membukanya
    # (tenancy gagal-ke-arah-aman), jadi diarahkan ke Inspektorat II (tim
    # pemilik sistem saat ini). Idempoten: hanya menyentuh baris NULL.
    for ddl in (
        f"UPDATE users SET inspektorat = '{DEFAULT_INSPEKTORAT}' WHERE inspektorat IS NULL",
        f"UPDATE penugasan SET inspektorat = '{DEFAULT_INSPEKTORAT}' WHERE inspektorat IS NULL",
    ):
        try:
            await db.execute(text(ddl))
        except Exception:  # noqa: BLE001
            pass
    await db.commit()

    # 2) Set username + password utk akun seed (insert akun baru spt PM bila belum ada).
    for u in SEED_USERS:
        row = (await db.execute(select(User).where(User.email == u["email"]))).scalar_one_or_none()
        if row is None:
            db.add(User(
                username=u["username"], email=u["email"], nama_lengkap=u["nama_lengkap"],
                nip=u["nip"], role_default=u["role_default"],
                password_hash=hash_password(DEV_PASSWORD),
                inspektorat=u.get("inspektorat", DEFAULT_INSPEKTORAT),
            ))
            continue
        if not getattr(row, "username", None):
            row.username = u["username"]
        if not getattr(row, "password_hash", None):
            row.password_hash = hash_password(DEV_PASSWORD)
        if not getattr(row, "inspektorat", None):
            row.inspektorat = u.get("inspektorat", DEFAULT_INSPEKTORAT)
    await db.commit()


async def init():
    print("[init_db] Membuat tabel ...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("[init_db] Seed users (upsert: insert kalau belum ada, update kalau role/nama/nip beda) ...")
    async with SessionLocal() as session:
        for u in SEED_USERS:
            existing = (
                await session.execute(select(User).where(User.email == u["email"]))
            ).scalar_one_or_none()
            if existing:
                # Upsert: cek apakah field-field penting perlu di-update
                # (mis. migrasi PM → PT di production yang sudah punya user existing)
                changed = []
                if existing.role_default != u["role_default"]:
                    changed.append(
                        f"role_default: {existing.role_default.value if hasattr(existing.role_default, 'value') else existing.role_default} → {u['role_default'].value}"
                    )
                    existing.role_default = u["role_default"]
                if existing.nama_lengkap != u["nama_lengkap"]:
                    changed.append(f"nama_lengkap: {existing.nama_lengkap!r} → {u['nama_lengkap']!r}")
                    existing.nama_lengkap = u["nama_lengkap"]
                if existing.nip != u["nip"]:
                    changed.append(f"nip: {existing.nip!r} → {u['nip']!r}")
                    existing.nip = u["nip"]
                if changed:
                    print(f"  ~ {u['email']} UPDATE: {', '.join(changed)}")
                else:
                    print(f"  - {u['email']} sudah ada, tidak ada perubahan")
                continue
            session.add(User(**u))
            print(f"  + {u['email']} ({u['role_default'].value})")
        await session.commit()
    print("[init_db] Selesai.")


if __name__ == "__main__":
    asyncio.run(init())

"""Pydantic schemas untuk request/response API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator

from app.models import DokumenStatus, PenugasanStatus, Role
from app.skills_registry import available_slugs, skill_exists


# ===== Auth =====
class LoginRequest(BaseModel):
    """Login (Workstream B): username + password.

    Jalur utama: `username` + `password` (diverifikasi bcrypt).
    Jalur LEGACY (dev, dipertahankan agar tak memutus alur lama): `role` (+`email`)
    tanpa password — hanya aktif bila APP_ENV != production.
    """
    username: str | None = None
    password: str | None = None
    role: Role | None = None
    email: EmailStr | None = None
    nip: str | None = None


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str | None = None
    email: str
    nama_lengkap: str
    nip: str
    role_default: Role


class SessionOut(BaseModel):
    user: UserOut
    role_aktif: Role
    token: str


class ChangePasswordRequest(BaseModel):
    """Ganti password sendiri (B4) — perlu sesi aktif."""
    old_password: str
    new_password: str


# ===== Penugasan =====
class PenugasanCreate(BaseModel):
    """Buat penugasan.

    Skill TIDAK lagi dipilih bebas: ia diturunkan dari `jenis_penugasan` +
    `sub_penugasan` lewat matriks di `app/deteksi_skill.py`. `skill` tetap
    diterima untuk (a) koreksi manual yang disengaja oleh Pengendali Teknis, dan
    (b) kompatibilitas pemanggil lama/SIMWAS yang sudah menyebut skill langsung.
    Salah satu harus ada — skill eksplisit, atau jenis+sub yang menghasilkannya.
    """

    obyek: str
    # Skill folder-driven (lihat skills_registry) — divalidasi ke registry.
    skill: str | None = None
    jenis_penugasan: str | None = None
    sub_penugasan: str | None = None
    nomor_st: str | None = None
    tanggal_st: str | None = None

    @field_validator("skill", mode="before")
    @classmethod
    def _skill_terdaftar(cls, v):
        # mode="before": v bisa berupa enum Skill (internal) atau str (dari API).
        # Ambil .value bila enum supaya tidak jadi "Skill.REVIU_PENGADAAN".
        if v is None or (isinstance(v, str) and not v.strip()):
            return None
        raw = getattr(v, "value", v)
        slug = str(raw).strip().lower()
        if not skill_exists(slug):
            raise ValueError(
                f"skill '{raw}' tidak terdaftar. Tersedia: {', '.join(available_slugs())}"
            )
        return slug

    @model_validator(mode="after")
    def _turunkan_skill(self):
        """Isi `skill` dari Jenis + Sub bila belum disebut eksplisit."""
        if self.skill:
            return self
        from app.deteksi_skill import skill_dari

        hasil = skill_dari(self.jenis_penugasan, self.sub_penugasan)
        if not hasil:
            raise ValueError(
                "Jenis Penugasan dan Sub Penugasan wajib diisi (atau sebutkan skill "
                "secara eksplisit) — skill ditentukan dari keduanya."
            )
        self.skill = hasil
        return self


class PenugasanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    kode: str
    obyek: str
    # String bebas (DB menyimpan str) — bisa skill di luar 2 pipeline lama.
    skill: str
    jenis_penugasan: str | None = None
    sub_penugasan: str | None = None
    nomor_st: str | None
    tanggal_st: str | None
    status: PenugasanStatus
    folder_path: str
    created_at: datetime
    updated_at: datetime


# ===== Dokumen =====
class DokumenOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    penugasan_id: int
    nama_file: str
    jenis: str | None
    sha256: str
    size_bytes: int
    status: DokumenStatus
    ingested_json_path: str | None
    error_message: str | None
    uploaded_at: datetime
    ingested_at: datetime | None


# ===== Agen =====
class AgentStartRequest(BaseModel):
    agent: str
    # "anggota_tim" | "ketua_tim"; QC SAIPI dipanggil otomatis dari kedua agen di atas


class AgentRunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    agent_name: str
    status: str
    tokens_in: int
    tokens_out: int
    started_at: datetime
    ended_at: datetime | None
    error_message: str | None


# ===== QC SAIPI =====
class QcSaipiOut(BaseModel):
    stage: str  # "kkp" | "lhp"
    overall_status: str  # "PASS" | "PASS_WITH_WARNINGS" | "BLOCKED_KRITIS"
    total_kritis: int
    total_peringatan: int
    total_needs_review: int
    total_ok: int
    laporan_path: str | None

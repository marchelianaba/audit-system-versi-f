"""SQLAlchemy models. Skema database minimal untuk prototype."""
from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Role(str, Enum):
    AT = "AT"  # Anggota Tim
    KT = "KT"  # Ketua Tim
    PT = "PT"  # Pengendali Teknis
    PM = "PM"  # Pengendali Mutu
    TU = "TU"  # Tata Usaha — administrasi pasca-persetujuan (Tahapan 8)
    ADMIN = "ADMIN"  # Administrator — akses file JSON mentah (digest/temuan/audit trail)


class Inspektorat(str, Enum):
    """Unit kerja pemilik penugasan — batas ISOLASI DATA.

    Inspektorat I–IV di lingkungan Inspektorat Jenderal Komdigi. Penugasan milik
    satu Inspektorat TIDAK boleh terbaca Inspektorat lain (lihat app/tenancy.py).
    """
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"


class Skill(str, Enum):
    REVIU_RKA_KL = "reviu-rka-kl"
    REVIU_PENGADAAN = "reviu-pengadaan"


class PenugasanStatus(str, Enum):
    DRAFT = "DRAFT"
    KP_DONE = "KP_DONE"          # PT simpan Kartu Penugasan → unlock PKP (v10.1: transplant tahapan v8)
    PKP_KT_DONE = "PKP_KT_DONE"  # KT simpan sasaran PKP, menunggu persetujuan PT (v10.1)
    PKP_DONE = "PKP_DONE"        # PT setujui PKP → unlock KKP (v10.1: semantik v8, bukan KT-save)
    INGESTING = "INGESTING"
    KKP_IN_PROGRESS = "KKP_IN_PROGRESS"
    KKP_QC = "KKP_QC"
    KKP_AT_DONE = "KKP_AT_DONE"  # semua AT submit KKP → menunggu persetujuan per-sasaran oleh KT (v10.1)
    KKP_DONE = "KKP_DONE"        # semua sasaran DISETUJUI_KT → unlock Konsep Laporan
    LHP_IN_PROGRESS = "LHP_IN_PROGRESS"
    LHP_QC = "LHP_QC"
    LHP_DONE = "LHP_DONE"


class DokumenStatus(str, Enum):
    UPLOADED = "UPLOADED"
    INGESTING = "INGESTING"
    READY = "READY"
    FAILED = "FAILED"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    # Login username+password (Workstream B). Nullable agar migrasi tabel lama aman.
    username: Mapped[str | None] = mapped_column(String(80), unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(200), nullable=True)
    nama_lengkap: Mapped[str] = mapped_column(String(200))
    nip: Mapped[str] = mapped_column(String(18))
    role_default: Mapped[Role] = mapped_column(String(16), default=Role.AT)
    # Unit kerja pemilik — batas isolasi data (Inspektorat I–IV).
    # Nullable demi migrasi aman; di-backfill oleh init_db (default: II).
    inspektorat: Mapped[str | None] = mapped_column(String(4), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Penugasan(Base):
    __tablename__ = "penugasan"

    id: Mapped[int] = mapped_column(primary_key=True)
    kode: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    obyek: Mapped[str] = mapped_column(String(400))
    skill: Mapped[Skill] = mapped_column(String(40))
    nomor_st: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tanggal_st: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Identitas penugasan ala SIMWAS. Keduanya MENENTUKAN skill lewat matriks
    # (app/deteksi_skill.py) — skill bukan lagi pilihan bebas Pengendali Teknis.
    # Nullable demi migrasi aman: penugasan lama tak punya keduanya.
    jenis_penugasan: Mapped[str | None] = mapped_column(String(40), nullable=True)
    sub_penugasan: Mapped[str | None] = mapped_column(String(80), nullable=True)
    # Jejak bila skill dikoreksi manual oleh PT (siapa, kapan, dari-ke apa).
    skill_override: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[PenugasanStatus] = mapped_column(String(40), default=PenugasanStatus.DRAFT, index=True)
    # ISOLASI DATA: penugasan hanya terlihat oleh pengguna Inspektorat yang sama.
    # Diisi otomatis dari inspektorat pembuat (PT) saat create. Penegakan: app/tenancy.py.
    inspektorat: Mapped[str | None] = mapped_column(String(4), nullable=True, index=True)
    ketua_tim_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    folder_path: Mapped[str] = mapped_column(String(400))
    context_md: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    dokumen: Mapped[list["Dokumen"]] = relationship(
        back_populates="penugasan", cascade="all, delete-orphan"
    )
    agent_runs: Mapped[list["AgentRun"]] = relationship(
        back_populates="penugasan", cascade="all, delete-orphan"
    )


class Dokumen(Base):
    __tablename__ = "dokumen"

    id: Mapped[int] = mapped_column(primary_key=True)
    penugasan_id: Mapped[int] = mapped_column(ForeignKey("penugasan.id"), index=True)
    nama_file: Mapped[str] = mapped_column(String(400))
    file_path: Mapped[str] = mapped_column(String(600))
    jenis: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # TOR, RAB, KAK, HPS, RFI, KONTRAK, ST, KP, PKP, OTHER
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    size_bytes: Mapped[int] = mapped_column(default=0)
    status: Mapped[DokumenStatus] = mapped_column(String(20), default=DokumenStatus.UPLOADED)
    ingested_json_path: Mapped[str | None] = mapped_column(String(600), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    penugasan: Mapped["Penugasan"] = relationship(back_populates="dokumen")


class DocumentCache(Base):
    """Cache hash-based untuk ingestion. Sekali sebuah PDF di-extract, file
    yang sama (apapun nama atau penugasan-nya) tidak perlu di-extract lagi."""

    __tablename__ = "document_cache"

    sha256: Mapped[str] = mapped_column(String(64), primary_key=True)
    jenis: Mapped[str] = mapped_column(String(40))
    ingested_json_path: Mapped[str] = mapped_column(String(600))
    extracted_by: Mapped[str] = mapped_column(String(40))  # "deterministic" | "haiku-fallback"
    extracted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TemuanReview(Base):
    """Status review per-temuan — layer HITL di atas `_KKP/temuan.json`.

    Sistem agen tetap tulis temuan ke `_KKP/temuan.json` lewat `append_temuan`,
    TAPI v7 layer filter berdasarkan status review sebelum render KKP/LHR.
    Status default `PENDING`; auditor (KT/PT/AT) approve via UI.

    `temuan_id` = `id_temuan` di `_KKP/temuan.json` (mis. 'T-001'). Unique
    per (penugasan_id, temuan_id) — 1 review per temuan.
    """

    __tablename__ = "temuan_review"

    id: Mapped[int] = mapped_column(primary_key=True)
    penugasan_id: Mapped[int] = mapped_column(ForeignKey("penugasan.id"), index=True)
    temuan_id: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    # PENDING | APPROVED | REJECTED | EDITED
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Edit-overlay: bila auditor edit field temuan via UI, simpan delta di sini.
    # Saat render KKP, V6 baca temuan.json hasil overlay (kode v7 menerapkan
    # edited_fields ke temuan asli sebelum panggil V6). Schema:
    #   { "judul_temuan": "...", "kondisi": "...", "kriteria": "...", "akibat": "..." }
    # Field yang tidak ada di edited_fields tetap pakai versi agen. Status biasanya
    # auto jadi "EDITED" saat edit pertama; auditor bisa approve/reject setelah edit.
    edited_fields: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Log append-only setiap edit MANUAL auditor (akuntabilitas). List of:
    #   {"at": iso, "by_user_id": int, "by_nama": str, "changes": {field: {"from": .., "to": ..}}}
    edit_log: Mapped[list | None] = mapped_column(JSON, nullable=True)
    reviewed_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class AgentRun(Base):
    """Setiap eksekusi agen di-log lengkap untuk audit trail."""

    __tablename__ = "agent_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    penugasan_id: Mapped[int] = mapped_column(ForeignKey("penugasan.id"), index=True)
    agent_name: Mapped[str] = mapped_column(String(40))
    # "ingestion" | "anggota_tim" | "qc_saipi_kkp" | "qc_saipi_lhp" | "ketua_tim"
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="running")
    # "running" | "completed" | "failed" | "blocked_kritis"
    input_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    tool_calls: Mapped[list | None] = mapped_column(JSON, nullable=True)
    tokens_in: Mapped[int] = mapped_column(default=0)
    tokens_out: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    penugasan: Mapped["Penugasan"] = relationship(back_populates="agent_runs")


class LhpReview(Base):
    """Reviu Konsep LHP oleh Pengendali Teknis / Pengendali Mutu (tahapan 6 — LRS LHP).

    Satu baris per aksi reviu (history terjaga). UI menampilkan baris terbaru.
    `status`:
      - APPROVED        — PT/PM menyetujui konsep LHP → tahapan 6 selesai.
      - NEEDS_REVISION  — PT/PM minta revisi; `catatan` memuat arahan perbaikan.
    """

    __tablename__ = "lhp_review"

    id: Mapped[int] = mapped_column(primary_key=True)
    penugasan_id: Mapped[int] = mapped_column(ForeignKey("penugasan.id"), index=True)
    reviewer_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewer_role: Mapped[str | None] = mapped_column(String(4), nullable=True)  # PT | PM
    status: Mapped[str] = mapped_column(String(20))  # APPROVED | NEEDS_REVISION
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class TlhpRekomendasi(Base):
    """Rekomendasi hasil pengawasan yang ditindaklanjuti (TLHP, Workstream C5).

    Sumber: (a) seed dummy dari fixture, (b) AUTO-INGEST dari rekomendasi LHP
    saat konsep LHP disetujui PT/PM (`_LHP/rekomendasi.json`) → menutup lingkaran
    laporan→TLHP. Aging (umur/warna/kritis) dihitung di route dari `tgl_lhp`.
    """

    __tablename__ = "tlhp_rekomendasi"

    id: Mapped[int] = mapped_column(primary_key=True)
    no_rek: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    penugasan_id: Mapped[int | None] = mapped_column(
        ForeignKey("penugasan.id"), nullable=True, index=True
    )
    temuan_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    asal_lhp: Mapped[str] = mapped_column(String(300), default="")
    satker: Mapped[str] = mapped_column(String(200), default="")
    satker_kode: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    substansi: Mapped[str] = mapped_column(Text, default="")
    pic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    tgl_lhp: Mapped[str | None] = mapped_column(String(20), nullable=True)   # YYYY-MM-DD
    deadline: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="BELUM", index=True)  # SUDAH/PROSES/BELUM/TIDAK_DAPAT
    bukti_tl: Mapped[str | None] = mapped_column(Text, nullable=True)
    sumber: Mapped[str] = mapped_column(String(20), default="dummy")  # dummy | ingest
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class LembarReviu(Base):
    """Lembar Reviu berjenjang (format INTEGRAL/SIMWAS) — checklist supervisi.

    `level`: "KT" (Reviu Ketua Tim atas Kertas Kerja, tahapan 4) atau
    "PT" (Reviu Pengendali Teknis atas Konsep LHP, tahapan 6).
    Aspek (A–D) baku per level (lihat `lembar_reviu.py`); di sini disimpan
    isian reviewer per aspek (`items`) + sign-off (paraf). 1 lembar per (penugasan, level).
    """

    __tablename__ = "lembar_reviu"

    id: Mapped[int] = mapped_column(primary_key=True)
    penugasan_id: Mapped[int] = mapped_column(ForeignKey("penugasan.id"), index=True)
    level: Mapped[str] = mapped_column(String(4), index=True)  # KT | PT
    # items = [{"kode":"A","status":"Sesuai","penyelesaian":"..."}]
    items: Mapped[list | None] = mapped_column(JSON, nullable=True)
    catatan: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewer_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewer_nama: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reviewer_nip: Mapped[str | None] = mapped_column(String(30), nullable=True)
    tanggal: Mapped[str | None] = mapped_column(String(40), nullable=True)
    diparaf: Mapped[bool] = mapped_column(default=False)  # sign-off
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

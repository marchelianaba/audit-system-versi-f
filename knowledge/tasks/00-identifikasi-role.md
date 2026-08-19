# Task 00 — Identifikasi Role (WAJIB tiap sesi)

> **Model**: `claude-haiku-4-5-20251001` — Tanya jawab singkat, tidak perlu penalaran berat.

## Tujuan
Memastikan Claude tahu **siapa** yang sedang bekerja dan **peran**nya di tim audit, sebelum task lain dijalankan. Role ini menentukan task & sasaran apa yang boleh diakses.

> Task ini **WAJIB dijalankan paling awal di setiap sesi** sebelum Task 01/03/04. Tanpa `_ROLE.md` valid, semua task lain akan menolak eksekusi.

---

## Aturan Role

| Role | Boleh Akses Task | Boleh Akses Skill |
|------|------------------|-------------------|
| **Anggota Tim** | Task 00, Task 01, Task 03 (KKP) | Semua 10 skill audit + skill pendukung wiki + script QC `qc_kkp_lhp.py --only kkp` |
| **Ketua Tim** | Task 00, Task 04 (LHP) | Semua skill yang dipakai untuk LHP + wiki + QC `--only lhp` |

Anggota tim **tidak boleh** menjalankan Task 04 (LHP). Ketua tim **tidak boleh** menjalankan Task 03 (KKP) — KKP adalah hasil kerja anggota tim sesuai pembagian sasaran di PKP.

> **Pengendali Mutu (PM)** dan **Pengendali Teknis (PT)** secara default disetarakan dengan Ketua Tim untuk akses sistem (boleh Task 04). Override manual bila diperlukan dengan field `role_override` di `_ROLE.md`.

---

## Langkah Eksekusi

### 1. Cek apakah `_ROLE.md` sudah ada di folder penugasan

Path: `penugasan/[nama-penugasan]/_ROLE.md`

- Jika **ada** dan masih valid (sesuai sesi hari ini & user yang sama) → load lalu konfirmasi ke user: *"Saya kenal Anda sebagai [Nama] ([Role]). Lanjut?"* Jika user setuju, lewati ke Task 01/03/04.
- Jika **tidak ada** atau **user berbeda** → jalankan langkah 2.

### 2. Tanya nama lengkap & role

Gunakan tool `AskUserQuestion`:

**Pertanyaan 1**: "Siapa nama lengkap Anda?" (free text via "Other")

**Pertanyaan 2**: "Apa peran Anda di penugasan ini?"
Opsi:
- Anggota Tim (AT)
- Ketua Tim (KT)
- Pengendali Teknis (PT)
- Pengendali Mutu (PM)

**Pertanyaan 3 (BARU — untuk integrasi INTEGRAL)**: "Berapa NIP Anda (18 digit)?"
- Free text via "Other"
- Validasi: harus 18 digit angka, tanpa spasi/strip
- NIP wajib untuk integrasi auto-inject KKP ke INTEGRAL (Task 03)
- Kalau auditor tidak ingat saat ini, boleh skip → field `nip:` di _ROLE.md akan kosong, tapi Task 03 auto-inject akan gagal sampai NIP dilengkapi

### 3. Validasi terhadap PKP

Jika `00-input/PKP-*.docx` atau `00-input/PKP-*.pdf` sudah ada (Task 01 sudah pernah jalan):
- Ekstrak daftar tim dari PKP (Pengendali Mutu, Pengendali Teknis, Ketua Tim, Anggota Tim 1..N).
- Cocokkan nama yang diinput user dengan daftar tim. Jika **tidak cocok**, tampilkan warning dan minta konfirmasi: *"Nama '[X]' tidak ditemukan di PKP. Lanjut sebagai guest atau perbaiki?"*
- Jika cocok, ambil role dari PKP (override input user) dan beri info: *"Sesuai PKP, role Anda adalah [Y]."*

### 4. Tulis `_ROLE.md`

Format:

```markdown
---
nama_lengkap: Sarah Aulia
role: Anggota Tim
role_kode: AT
nip: 198501012010011001
role_validated_against_pkp: true
session_start: 2026-05-02T14:30:00+07:00
---

# Sesi Aktif — Sarah Aulia (Anggota Tim)

Penugasan: 2026-05-001-reviu-pengadaan-bakti
Sasaran yang diassign ke Anda (dari PKP, akan diisi Task 01):
- (belum dijalankan Task 01)
```

### 5. Log ke audit trail

Panggil `scripts/audit_trail.py log-event` dengan:
- `action`: `ROLE_LOGIN`
- `actor`: `{nama, role}`
- `target`: `_ROLE.md`
- `payload`: `{validated_against_pkp: bool, source: "input"|"pkp_match"}`

### 6. Konfirmasi ke user

Tampilkan ringkasan:
> "Selamat datang, **Sarah Aulia** (Anggota Tim). Anda terdaftar di penugasan **2026-05-001-reviu-pengadaan-bakti**. Saya akan melanjutkan ke Task 01 (Inisiasi) untuk membaca ST + KP + PKP. LANJUT / KOREKSI?"

---

## Aturan Penolakan (deny rules)

Saat task lain dipanggil:

```python
# pseudocode di tiap task:
role = read_role_md()
if not role:
    raise "Jalankan Task 00 dulu — _ROLE.md belum ada."

allowed_tasks = ROLE_PERMISSIONS[role.role_kode]  # AT: [00,01,03], KT/PT/PM: [00,04]
if current_task not in allowed_tasks:
    raise f"Role '{role.role}' tidak boleh menjalankan {current_task}. Minta {required_role} untuk login."
```

---

## Output

- `penugasan/[nama]/_ROLE.md` — sumber kebenaran role sesi ini
- 1 entry ke `_AUDIT-TRAIL/events.jsonl` (action=ROLE_LOGIN)

## Konfirmasi auditor

Setelah Task 00 selesai, tanya:
> "Apakah Anda ingin saya lanjut ke **Task 01 (Inisiasi)** sekarang? LANJUT / TUNGGU"

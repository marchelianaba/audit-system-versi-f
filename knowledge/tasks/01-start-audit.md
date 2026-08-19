# Task 01 — Inisiasi Penugasan (v4)

> **Model**: `claude-haiku-4-5-20251001` — Routing dan ekstraksi struktural, tidak butuh penalaran berat.

> **Hanya boleh dijalankan oleh role: Anggota Tim (AT)**. Akan ditolak oleh `scripts/role_check.py` jika dipanggil oleh ketua tim.

## Tujuan
Membaca tiga dokumen input yang **sudah disiapkan auditor di sistem INTEGRAL** (Surat Tugas, Kartu Penugasan, Program Kerja Pengawasan), menentukan skill, mengekstrak konteks penugasan, dan mengekstrak **pembagian sasaran ke anggota tim** ke dalam `_PKP/sasaran-assignment.json`. Tidak ada lagi generation KP atau PKP.

---

## ⛔ ATURAN PROTEKSI SISTEM

**Selama eksekusi penugasan apapun, Claude DILARANG KERAS:**
- Membuat, mengubah, atau menghapus file di `audit-system-v4/tasks/`, `skills/`, `checklists/`, `schemas/`, `scripts/`, `wiki/`
- Mengubah `audit-system-v4/README.md`, `CHANGELOG-v4.md`

Output Claude HANYA boleh ditulis ke folder penugasan aktif:
```
penugasan/[nama-penugasan]/
  ├── 00-input/            ← (input auditor: ST, KP, PKP, dokumen pendukung)
  ├── _ROLE.md             ← (Task 00)
  ├── context.md           ← (Task 01)
  ├── _PKP/
  │   └── sasaran-assignment.json   ← (Task 01)
  ├── _KKP/
  │   ├── temuan.json      ← (Task 03 — sumber kebenaran inject INTEGRAL)
  │   └── KKP-[nama-anggota].docx   ← (Task 03 — view auditor)
  ├── _LHP/
  │   └── LHP-substansi.docx        ← (Task 04)
  └── _AUDIT-TRAIL/
      └── events.jsonl     ← (semua aksi sepanjang penugasan)
```

---

## Pre-Check (WAJIB sebelum mulai)

1. **Role check**:
   ```bash
   python3 scripts/role_check.py --penugasan penugasan/[nama] --task 01
   ```
   Jika exit ≠ 0 → STOP, suruh user jalankan Task 00.

2. **Cek input lengkap**:
   Folder `00-input/` harus berisi minimal:
   - 1 file Surat Tugas (`ST-*.pdf` atau `ST-*.docx`)
   - 1 file Kartu Penugasan (`KP-*.pdf` atau `KP-*.docx`)
   - 1 file Program Kerja Pengawasan (`PKP-*.pdf` atau `PKP-*.docx`)

   Jika ada yang kurang → STOP, minta auditor download dari INTEGRAL dan letakkan di `00-input/`.

3. **Log start**:
   ```bash
   python3 scripts/audit_trail.py log-event --penugasan penugasan/[nama] \
     --action TASK_STARTED --task 01 --target context.md
   ```

---

## Langkah Eksekusi

### 1. Baca Surat Tugas (`00-input/ST-*`)

Ekstrak:
- Nomor ST dan tanggal ST
- Jenis pengawasan (lihat tabel routing di bawah)
- Obyek pengawasan
- Periode pengawasan
- Tim: Pengendali Mutu, Pengendali Teknis, Ketua Tim, Anggota
- Dasar penugasan (PKPT / Nota Dinas)
- Tujuan dan sasaran (high-level)

### 2. Baca Kartu Penugasan (`00-input/KP-*`)

Ekstrak:
- Tingkat risiko
- Penerima LHP (untuk kepala surat)
- Hari penugasan & estimasi mandays
- Catatan khusus dari Pengendali Mutu (jika ada)

### 3. Baca Program Kerja Pengawasan (`00-input/PKP-*`) — **paling penting di v4**

Ekstrak **per sasaran**:
- `sasaran_id` (S-01, S-02, ..., diberikan berurutan)
- `deskripsi` sasaran
- `langkah_kerja` (list)
- `assigned_to` — **siapa anggota tim yang ditugaskan kerjakan sasaran ini**
  - Bisa lebih dari 1 anggota per sasaran
  - Nama harus persis sama dengan yang ada di tabel tim PKP

> **Bila PKP tidak menuliskan pembagian sasaran ke anggota** → STOP dan minta auditor (Ketua Tim) menulis pembagian itu di INTEGRAL terlebih dahulu, lalu unduh ulang PKP.

### 4. Tentukan Skill

| Jenis Pengawasan | Kata Kunci di ST/KP | Skill | Kolom KKP | Paradigma |
|---|---|---|---|---|
| **Audit Pengadaan** | "audit pengadaan", "audit PBJ", "audit kinerja pengadaan" | `skills/audit-pengadaan/` | No, Judul, Kondisi, Kriteria, **Sebab**, Akibat | Keyakinan Memadai |
| **Audit Kinerja** | "audit kinerja", "audit program", "audit efektivitas" | `skills/audit-kinerja/` | No, Judul, Kondisi, Kriteria, **Sebab**, Akibat | Keyakinan Memadai |
| **Reviu Pengadaan** | "reviu pengadaan", "reviu perencanaan", "reviu kontrak" | `skills/reviu-pengadaan/` | No, Judul, Kondisi, Kriteria, Akibat | Keyakinan Terbatas |
| **Reviu RKA/KL** | "reviu rka", "reviu anggaran" | `skills/reviu-rka-kl/` | No, Judul, Kondisi, Kriteria, Akibat | Keyakinan Terbatas |
| **Pemantauan Pengadaan** | "pemantauan pengadaan", "monitoring kontrak" | `skills/pemantauan-pengadaan/` | No, Judul, Kondisi, Kriteria | Pemantauan |
| **Pemantauan TLHP** | "pemantauan tindak lanjut", "TLHP" | `skills/pemantauan-tindak-lanjut/` | No, Judul, Kondisi, Kriteria | Pemantauan |
| **Evaluasi SAKIP** | "evaluasi sakip", "evaluasi akip" | `skills/evaluasi-sakip/` | LKE Excel | Keyakinan Terbatas |
| **Evaluasi SPIP** | "evaluasi spip", "maturitas spip" | `skills/evaluasi-spip/` | LKE Excel | Keyakinan Terbatas |
| **Evaluasi RB** | "evaluasi rb", "reformasi birokrasi" | `skills/evaluasi-reformasi-birokrasi/` | LKE Excel | Keyakinan Terbatas |
| **Evaluasi Manajemen Risiko** | "evaluasi mr", "manajemen risiko" | `skills/evaluasi-manajemen-risiko/` | No, Judul, Kondisi, Kriteria, Akibat | Keyakinan Terbatas |
| **Konsultasi Pengadaan** | "konsultasi", "pendapat teknis" | `skills/konsultasi-pengadaan/` | No, Pertanyaan, Analisis, Dasar Hukum, Rekomendasi | Konsultasi |

### 5. Tulis `context.md`

Format sama seperti v3 (lihat lampiran di akhir file ini), DENGAN penambahan:

```
Status            : TAHAP 1 — INISIASI (v4)
Sumber KP/PKP     : INTEGRAL (di-upload manual ke 00-input/)
Pembagian Sasaran : lihat _PKP/sasaran-assignment.json
```

### 6. Tulis `_PKP/sasaran-assignment.json`

Sesuai schema `schemas/sasaran-assignment.schema.json` (lihat juga `schemas/examples/sasaran-assignment-sample.json`).

Validasi sebelum lanjut:
```bash
python3 scripts/validate_kkp_json.py penugasan/[nama]/_PKP/sasaran-assignment.json
```
Jika FAILED → perbaiki ekstraksi sebelum konfirmasi auditor.

### 7. Update `_ROLE.md` dengan daftar sasaran user

Setelah `sasaran-assignment.json` ada, edit `_ROLE.md` dan isi bagian "Sasaran yang diassign" dengan sasaran-sasaran yang `assigned_to` mencantumkan nama_lengkap user saat ini.

### 7b. Generate placeholder _QA-SAIPI artifacts (v4.0.4)

Otomatis tulis placeholder file QA SAIPI agar 4 NEEDS_REVIEW dari `qc_saipi.py` sudah terjawab sebelum analisis Task 03 mulai. Tanpa langkah ini, KKP-stage QC akan iterasi 1-2x.

```bash
python3 scripts/init_qa_artifacts.py --penugasan penugasan/[nama]
```

Outputnya: `_QA-SAIPI/deklarasi-independensi.md`, `jawaban-needs-review.md`, `justifikasi.md`. Auditor tetap diminta review/koreksi sebelum gate Task 04, tapi tidak perlu generate dari nol.

### 7c. Preflight QC SAIPI (v4.0.4)

Cek subset rules `REN-001..REN-007` (tujuan terisi, ruang lingkup terisi, KP/PKP ada di 00-input/, ≥1 sasaran, dst) sebelum gate. Tujuan: menutup gap KRITIS context.md yang baru muncul saat Task 03/04 (mahal di-iterasi karena sudah ada temuan).

```bash
python3 scripts/qc_saipi.py --penugasan penugasan/[nama] --preflight-context
# exit 0 → context.md OK, lanjut ke gate
# exit 2 → ada KRITIS, perbaiki context.md dan re-run
```

### 8. Log events ke audit trail (v4.0.4 — pakai log-batch)

Hemat 5+ subprocess overhead dengan satu call batch:

```bash
python3 scripts/audit_trail.py log-batch --penugasan penugasan/[nama] --events '[
  {"action": "TASK_STARTED",   "task": "01", "target": "context.md"},
  {"action": "FILE_GENERATED", "task": "01", "target": "context.md"},
  {"action": "FILE_GENERATED", "task": "01", "target": "_PKP/sasaran-assignment.json", "payload": {"jumlah_sasaran": 3, "schema_valid": true}},
  {"action": "FILE_GENERATED", "task": "01", "target": "_QA-SAIPI/deklarasi-independensi.md"},
  {"action": "TASK_COMPLETED", "task": "01", "target": "context.md", "payload": {"skill": "reviu-pengadaan"}}
]'
```

Backward-compatible — `log-event` tetap berfungsi untuk single event.

### 9. Konfirmasi ke auditor (anggota tim)

```
=== KONFIRMASI INISIASI PENUGASAN (v4) ===

Nomor ST         : [xxx]
Tanggal ST       : [tanggal]
Obyek            : [nama obyek]
Jenis            : [jenis pengawasan]
Skill            : [nama skill]
Penerima LHP     : [jabatan — dari KP]
Tingkat Risiko   : [Tinggi/Sedang/Rendah — dari KP]

Tim:
  Pengendali Mutu  : [nama]
  Pengendali Teknis: [nama]
  Ketua Tim        : [nama]
  Anggota          : [nama-nama]

Sasaran (dari PKP) — total [N]:
  S-01 : [deskripsi]   → ditugaskan ke: [nama-nama AT]
  S-02 : [deskripsi]   → ditugaskan ke: [nama-nama AT]
  ...

📌 Anda login sebagai: [Nama Anda] (Anggota Tim)
   Sasaran Anda: [S-XX, S-YY] — totalnya [k] sasaran.
   Anggota lain dengan sasaran masing-masing:
     - [Nama1] → [S-AA, S-BB]
     - [Nama2] → [S-CC]

Alur selanjutnya:
  ② Task 03 → Anda kerjakan KKP HANYA untuk sasaran Anda.
  ③ Task 04 → Setelah SEMUA anggota selesai KKP, Ketua Tim ([nama KT])
              login dan menjalankan Task 04 untuk LHP.

Ketik LANJUT untuk mulai Task 03 (KKP) dengan sasaran Anda.
Ketik KOREKSI kalau ada data yang salah.
```

### 10. Catat gate

```bash
python3 scripts/audit_trail.py log-event --penugasan penugasan/[nama] \
  --action GATE_PASSED --task 01 --target context.md \
  --payload '{"konfirmasi": "LANJUT"}'
```

---

## Output

- `context.md`
- `_PKP/sasaran-assignment.json` (valid terhadap schema)
- `_ROLE.md` di-update dengan daftar sasaran user
- 4-6 events di `_AUDIT-TRAIL/events.jsonl`

## Catatan

- Jika ST/KP/PKP tidak terbaca → tanyakan, jangan menebak.
- Jika ada amandemen ST → pakai yang terbaru, catat di `context.md`.
- Bila auditor menambahkan sasaran baru di INTEGRAL setelah Task 01 selesai → minta auditor unduh ulang PKP & jalankan Task 01 lagi (akan over-write `sasaran-assignment.json` dengan log update).

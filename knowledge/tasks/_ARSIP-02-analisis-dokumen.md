# Task 02 — Validasi Dokumen dan Index

> **Model**: `claude-haiku-4-5-20251001` — Checklist dan validasi administratif, tidak memerlukan analisis mendalam.

## Tujuan
Periksa kelengkapan dokumen yang diupload, validasi terhadap checklist per jenis pengawasan, buat index dokumen, dan minta konfirmasi auditor sebelum melanjutkan ke analisis.

---

## Langkah Eksekusi

### 1. Baca `context.md`
Muat kembali: skill yang aktif, jenis pengawasan, obyek, nomor ST.

### 2. Baca checklist dokumen
Buka file: `checklists/[nama-skill].md`

Contoh:
- `checklists/reviu-pengadaan.md`
- `checklists/audit-pengadaan.md`
- `checklists/pemantauan-pengadaan.md`
- `checklists/konsultasi-pengadaan.md`

File ini berisi daftar dokumen **WAJIB**, **PENTING**, dan **OPSIONAL** untuk jenis pengawasan ini.

### 3. Baca SKILL.md + references/
Baca `skills/[nama-skill]/SKILL.md` dan file di `references/` untuk memuat kriteria analisis.

### 4. Index semua dokumen yang ada

Baca **hanya folder yang relevan** dengan jenis pengawasan (hemat token):

| Folder | Baca untuk skill ini? |
|--------|-----------------------|
| `00-surat-tugas/` | ✅ Selalu |
| `01-peraturan-internal/` | ✅ Jika ada — baca hanya nama file |
| `02-kontrak/` | ✅ Reviu pengadaan: baca jika ada kontrak pembanding |
| `03-perencanaan/` | ✅ Selalu (dokumen utama) |
| `04-pelaksanaan/` | ❌ SKIP untuk reviu/audit perencanaan |
| `05-keuangan/` | ❌ SKIP untuk reviu/audit perencanaan |

> Folder output `_KP/`, `_PKP/`, `_KKP/`, `_LHP/` akan dibuat secara bertahap oleh Task 02b, 03, 04, dan 05. Jangan khawatir jika belum ada.

Untuk setiap file yang ditemukan, catat:
- Nama file
- Jenis dokumen (KAK / kontrak / HPS / laporan progres / dll)
- Tanggal dokumen (jika tertera)
- Nilai Rp (jika ada)

> **Panduan membaca PDF besar**: Jangan baca semua halaman berurutan. Gunakan `pages` parameter secara bertarget:
> - Halaman 1–3: Identitas dokumen (judul, tanggal, nilai)
> - Halaman latar belakang: Cek nilai SLA, periode, tujuan
> - Halaman spesifikasi teknis: Cek SLA, kapasitas, standar
> - Halaman klausul khusus (migrasi, SLA, pembayaran): Cek komponen biaya
> Jangan baca halaman yang tidak relevan dengan aspek yang diperiksa.

### 5. Validasi terhadap checklist

Cocokkan dokumen yang ditemukan dengan checklist. Tandai status setiap item:

| Status | Simbol | Arti |
|--------|--------|------|
| Tersedia | ✅ | Dokumen ditemukan di folder |
| Tidak ada | ❌ | Dokumen tidak ditemukan |
| Tidak dapat dibaca | ⚠️ | File ada tapi tidak bisa diakses (password/format) |

Kategorikan setiap dokumen yang tidak ada berdasarkan tingkatnya:
- **KRITIS** → reviu/audit tidak dapat dilanjutkan
- **PERINGATAN** → aspek tertentu tidak dapat dinilai (catat sebagai keterbatasan)
- **INFORMASI** → tidak mempengaruhi kedalaman analisis

### 6. Simpan index + ringkasan dokumen

Buat file `_KKP/index-dokumen.md` dengan isi:

```
# Index Dokumen — [Nama Obyek]
Tanggal: [tanggal hari ini]
Skill: [nama skill]

## Dokumen Tersedia
[daftar dengan jenis, nama file, tanggal, dan nilai jika ada]

## Keterbatasan Dokumen
[daftar dokumen yang tidak tersedia beserta tingkat dampaknya]
```

**⚡ EFISIENSI — Tambahkan bagian ringkasan isi dokumen** (ini menghindari re-reading di Task 03):

```
## Ringkasan Isi Dokumen (untuk Task 03)

### KAK [nama file]
- Obyek: [nama paket pengadaan]
- Periode: [periode pelaksanaan]
- Nilai estimasi: [nilai jika ada di KAK]
- SLA yang disebutkan di Latar Belakang: [nilai]
- SLA yang disebutkan di Persyaratan Teknis: [nilai]
- Metode pemilihan: [Tender/E-Purchasing/dll]
- Ada klausul migrasi?: [Ya/Tidak] — jika Ya: [ringkasan singkat]
- Poin penting lain: [butir-butir spesifik yang relevan]

### HPS [nama file]
- Nilai total: [nilai]
- Tanggal penetapan: [tanggal]
- Komponen utama: [daftar komponen dan nilai persentase]
- Ada komponen biaya migrasi/transisi?: [Ya/Tidak]
- Periode yang dihitung: [periode]
- Metode survei: [RFI/e-katalog/dll, jumlah sumber]

### Kontrak Pembanding [nama file, jika ada]
- Penyedia: [nama]
- Nilai: [nilai]
- Periode: [periode]
- SLA: [nilai]
- Relevansi sebagai pembanding: [apa yang bisa dikomparasi]

### Dokumen lain: [sebutkan jika ada]
```

> **Mengapa ini penting**: Task 03 (KKP) memerlukan analisis mendalam dokumen yang sama. Jika ringkasan sudah ada di sini, Task 03 tidak perlu membaca ulang — hemat 15–20% token total workflow. Isi bagian ini sedetail yang diperlukan untuk analisis KKP.

### 7. Tampilkan ringkasan validasi kepada auditor

```
=== VALIDASI DOKUMEN ===
Obyek     : [nama obyek]
Jenis     : [jenis pengawasan]
Skill     : [nama skill]

WAJIB:
  ✅ W1 — [nama dokumen] : [nama file yang ditemukan]
  ❌ W2 — [nama dokumen] : TIDAK DITEMUKAN  ← KRITIS
  ...

PENTING:
  ✅ P1 — [nama dokumen] : [nama file]
  ❌ P2 — [nama dokumen] : TIDAK DITEMUKAN  ← aspek [xxx] tidak dapat dinilai
  ...

OPSIONAL:
  ✅ O1 — [nama dokumen] : [nama file]
  ❌ O2 — [nama dokumen] : tidak tersedia (tidak mempengaruhi analisis)
  ...
```

Kemudian tampilkan salah satu notifikasi berikut (sesuai kondisi):

**Jika ada dokumen KRITIS yang tidak ada:**
```
❌ DOKUMEN KRITIS TIDAK LENGKAP

[Jenis pengawasan] tidak dapat dilanjutkan karena dokumen berikut tidak ditemukan:
  • [daftar dokumen kritis]

Mohon upload dokumen tersebut ke folder yang sesuai:
  • [nama dokumen] → simpan di folder [nama folder]

Setelah dokumen diupload, ketik ULANG untuk memeriksa ulang kelengkapan.
```

**Jika ada dokumen PENTING yang tidak ada (tapi tidak kritis):**
```
⚠️ DOKUMEN TIDAK LENGKAP — ANALISIS TERBATAS

[Jenis pengawasan] dapat dilanjutkan, namun aspek berikut tidak dapat dinilai:
  • [dokumen P1 tidak ada] → aspek [xxx] tidak dapat dinilai
  • [dokumen P2 tidak ada] → aspek [yyy] tidak dapat dinilai

Keterbatasan ini akan dicatat dalam laporan.

Pilihan:
  A) Ketik LANJUT  → mulai analisis dengan dokumen yang ada
  B) Upload dokumen tambahan terlebih dahulu, lalu ketik ULANG
```

**Jika semua dokumen wajib tersedia:**
```
✅ DOKUMEN SIAP

Semua dokumen wajib tersedia. [X] dokumen penting tersedia, [Y] dokumen opsional tersedia.

Langkah selanjutnya: Task 02b — Generate Kartu Penugasan (KP) + Program Kerja Pengawasan (PKP).
Ketik LANJUT untuk melanjutkan ke Task 02b.
```

---

## Output
- `_KKP/index-dokumen.md` — index dan status kelengkapan dokumen
- Konfirmasi auditor (LANJUT / ULANG) untuk lanjut ke Task 02b (KP + PKP)

## Catatan
- Jika folder penugasan tidak mengikuti struktur standar (00–05), tetap baca semua file yang ada dan sesuaikan
- Jika file tidak dapat dibaca (password, format tidak didukung): catat sebagai `⚠️ Tidak dapat dibaca`
- Untuk reviu yang dokumennya dikirim via chat (bukan folder), catat dari chat context dan tidak perlu validasi folder
- Auditor selalu dapat mengoverride peringatan dengan mengetik LANJUT — catatan keterbatasan tetap masuk laporan

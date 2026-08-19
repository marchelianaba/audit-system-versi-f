# Task 02b — Generate Survey Pendahuluan (jika perlu) + Kartu Penugasan (KP) + Program Kerja Pengawasan (PKP)

> **Model**: `claude-haiku-4-5-20251001` untuk KP + PKP (pengisian template). Untuk Survey Pendahuluan audit-kinerja, **gunakan `claude-sonnet-4-6`** karena memerlukan analisis risiko dan penajaman sasaran.

## Tujuan
Menyusun dokumen perencanaan formal pengawasan:
0. **Memo Survey Pendahuluan (SP)** — **WAJIB untuk audit-kinerja**; opsional untuk jenis pengawasan lain yang memerlukan penajaman sasaran. Memuat pemetaan risiko, penajaman sasaran, dan ruang lingkup terukur.
1. **Kartu Penugasan (KP)** — dokumen identitas penugasan yang disetujui Pengendali Teknis
2. **Program Kerja Pengawasan (PKP)** — rencana kerja terstruktur per sasaran, disetujui Pengendali Teknis + Ketua Tim

---

## Prasyarat
- `context.md` sudah ada (hasil Task 01) — konfirmasi LANJUT sudah diterima
- Skill yang aktif sudah dibaca (SKILL.md + references/)

> **Catatan**: Tahap validasi dokumen (Task 02) telah dihilangkan April 2026 untuk efisiensi token. Kelengkapan dokumen tidak divalidasi di tahap ini; Task 03 akan melakukan file listing + ringkasan inline saat akan menganalisis. Khusus audit-kinerja, SP di bawah tetap memiliki prasyarat dokumen programnya sendiri.

---

## 🧭 Routing Berdasarkan Jenis Pengawasan

Sejak April 2026, pembuatan KP + PKP dibagi menjadi **dua jalur** sesuai jenis pengawasan:

| Jalur | Jenis Pengawasan | Cara Pembuatan |
|-------|------------------|----------------|
| **A — Bespoke (disusun ulang per penugasan)** | `audit-kinerja`, `audit-pengadaan`, `reviu-pengadaan`, `konsultasi-pengadaan` | KP + PKP dirancang ulang tiap penugasan karena sasaran/langkah kerjanya sangat tergantung program/paket yang diaudit. Untuk audit-kinerja **wajib Memo SP** terlebih dahulu. |
| **B — Template Standar (find-replace placeholder)** | `reviu-rka-kl`, `pemantauan-pengadaan`, `evaluasi-sakip`, `evaluasi-spip`, `evaluasi-reformasi-birokrasi`, `evaluasi-manajemen-risiko` | KP + PKP sudah terstandar di `templates/kp-pkp/[jenis]/`. Hanya placeholder (objek, tanggal, tahun, tim, tingkat risiko) yang diganti tiap penugasan. |

**Tentukan jalur dari `context.md` → field `Skill :`** sebelum mulai.
- Jalur A → ikuti BAGIAN A-PRE (jika audit-kinerja) → BAGIAN A (KP bespoke) → BAGIAN B (PKP bespoke)
- Jalur B → **lewati BAGIAN A-PRE / A / B** → langsung ke **BAGIAN C — TEMPLATE STANDAR**

---

## BAGIAN A-PRE — SURVEY PENDAHULUAN (WAJIB untuk Audit Kinerja)

> **Trigger:** Jika `context.md` memuat `Skill : audit-kinerja` (atau sub-skill `audit-kinerja-[program]`), lakukan BAGIAN A-PRE terlebih dahulu sebelum Bagian A (KP) dan Bagian B (PKP). Untuk skill lain, lewati bagian ini kecuali auditor secara eksplisit meminta survey pendahuluan.

### Dasar
Standar Audit APIP (AAIPI) — Standar Pelaksanaan 3100. Sasaran dan ruang lingkup audit kinerja **tidak boleh disalin verbatim dari ST** tanpa penajaman berbasis risiko.

### Prasyarat tambahan untuk Survey Pendahuluan
Pastikan dokumen berikut tersedia di folder penugasan. Jika belum, **minta auditor mengunggah** sebelum melanjutkan:
- Proses bisnis program / SOP internal
- Perjanjian Kinerja (PK) tahun diaudit + IKU + target
- LKj tahun lalu (untuk baseline)
- Data realisasi kinerja berjalan (B06/B09/B12 atau e-monev)
- DIPA/RKA program + laporan realisasi anggaran
- TOR/KAK program
- Hasil audit/reviu sebelumnya (jika ada)

### Format Nomor Memo SP
```
SP/[nomor-penugasan]/IJ.3/KP.01.06/[bulan]/[tahun]
Contoh: SP/254/IJ.3/KP.01.06/11/2025
```

### Langkah Pelaksanaan Survey Pendahuluan

1. **Petakan logika intervensi program** dari TOR/KAK + proses bisnis:
   ```
   Input (anggaran, SDM) → Proses (tahapan) → Output (hasil langsung) → Outcome (manfaat)
   ```
2. **Research online — Benchmarking & Best Practice** (lihat detail di `skills/audit-kinerja/SKILL.md` bagian "Research Online — Benchmarking & Best Practice"):
   - Identifikasi 3–5 kata kunci inti program dari `context.md` + TOR/KAK.
   - Jalankan WebSearch untuk **keempat jenis** research: (a) benchmark K/L lain, (b) best practice internasional, (c) regulasi & pedoman teknis terbaru, (d) hasil audit BPK/BPKP + riset akademis.
   - Untuk hasil yang relevan, baca sumber asli via WebFetch — jangan menyimpulkan dari snippet saja.
   - Catat per temuan: **judul sumber, URL lengkap, tanggal akses (hari ini), ringkasan faktual 2–4 kalimat, relevansi 1 kalimat**.
   - Filter sumber: pertahankan sumber otoritatif (`.go.id`, BPK/BPKP, OECD/World Bank/INTOSAI, jurnal akademis); tolak blog tanpa kredensial / SEO farm / media sosial.
   - Jika salah satu dari 4 jenis tidak menghasilkan sumber memadai → **catat eksplisit** di Memo SP bagian 2.5 (jangan kosongkan diam-diam).
3. **Analytical review awal** berbasis data:
   - Target IKU di PK vs realisasi terkini (dari LKj/e-monev)
   - % realisasi anggaran vs % capaian output fisik
   - Tren tahun lalu vs tahun ini
   - **Perbandingan dengan benchmark K/L lain atau best practice** (dari hasil Langkah 2)
4. **Pemetaan risiko kinerja** — untuk setiap simpul logika intervensi, catat risiko efektivitas dan efisiensi + tingkat risiko (Tinggi/Sedang/Rendah). Kolom "Dasar Risiko" menyebutkan apakah risiko bersumber dari dokumen internal atau dari benchmark/best practice (sebut baris referensi).
5. **Pilih 2–4 area fokus** berdasarkan risiko tertinggi.
6. **Tajamkan sasaran audit** dari ST:
   - Baca sasaran ST (di `context.md`)
   - Reformulasikan per area fokus menjadi sasaran yang **spesifik, terukur, berbasis risiko**
   - Jika perlu menambah/mengurangi sasaran dari ST — eksplisitkan alasannya
7. **Tetapkan ruang lingkup** yang terukur: periode diaudit, unit/lokasi sampel, aspek 3E yang diuji, batasan audit.
8. **Susun hipotesis audit awal** — dugaan temuan per sasaran → ini menjadi dasar langkah kerja PKP.

### Output — File Word Memo SP

Buat file: `_SP/SP-[nomor-ST].docx` dengan struktur:

```
                MEMO SURVEY PENDAHULUAN
         SP/[nomor]/IJ.3/KP.01.06/[bulan]/[tahun]

A. Dasar Penugasan       : [Nomor ST + tanggal]
B. Program yang Diaudit  : [Nama program]
C. Unit Pelaksana        : [Unit]
D. Periode yang Diaudit  : [tanggal]
E. Tim Survey            : [Ketua Tim + Anggota]

1. GAMBARAN UMUM PROGRAM
   1.1 Tujuan program (dari TOR/KAK)
   1.2 Logika intervensi (Input → Proses → Output → Outcome)
   1.3 Anggaran dan sumber daya (nominal + sumber data)
   1.4 IKU utama dan target PK

2. BENCHMARKING & BEST PRACTICE (hasil research online)
   2.1 Benchmark K/L lain di Indonesia
       | No | Sumber | URL | Tgl Akses | Ringkasan Faktual | Relevansi |
   2.2 Best Practice Internasional (OECD / World Bank / INTOSAI / dll)
       | No | Sumber | URL | Tgl Akses | Ringkasan Faktual | Relevansi |
   2.3 Regulasi & Pedoman Teknis Terbaru (Bappenas / KemenPAN-RB / Kemenkeu / dll)
       | No | Sumber | URL | Tgl Akses | Ringkasan Faktual | Relevansi |
   2.4 Hasil Audit BPK/BPKP & Riset Akademis atas Program Sejenis
       | No | Sumber | URL | Tgl Akses | Ringkasan Faktual | Relevansi |
   2.5 Catatan: sumber yang TIDAK ditemukan / perlu verifikasi auditor
       [daftar eksplisit — jangan kosongkan diam-diam jika salah satu jenis tidak ketemu]

3. PEMETAAN RISIKO KINERJA
   [Tabel]
   | No | Simpul | Area Risiko | Risiko Efektivitas | Risiko Efisiensi | Tingkat | Dasar Risiko (internal / Bagian 2.x) |
   |----|--------|-------------|---------------------|-------------------|---------|---------------------------------------|

4. ANALYTICAL REVIEW AWAL
   4.1 Target vs Realisasi IKU
       [Tabel IKU | Target PK | Realisasi | % Capaian | Sumber]
   4.2 Serapan Anggaran vs Capaian Fisik
       [Tabel Komponen | % Realisasi Keu | % Realisasi Fisik | Delta]
   4.3 Perbandingan dengan Benchmark / Best Practice
       [ringkas perbandingan angka/pendekatan dengan Bagian 2; sebut baris referensi]
   4.4 Anomali / isu yang teridentifikasi

5. AREA FOKUS AUDIT (2–4 area)
   5.1 [Area 1 — alasan dipilih + referensi Bagian 2 jika relevan]
   5.2 [Area 2 — alasan dipilih + referensi Bagian 2 jika relevan]
   ...

6. PENAJAMAN SASARAN AUDIT
   Sasaran dari ST (asli):
     1. [verbatim dari ST]
     2. [verbatim dari ST]
   Sasaran setelah penajaman:
     1. [sasaran spesifik untuk Area 1]
     2. [sasaran spesifik untuk Area 2]
     ...
   Penjelasan penajaman:
     [alasan singkat mengapa sasaran diubah/ditajamkan]

7. RUANG LINGKUP TERUKUR
   - Periode diaudit        : [tanggal mulai s.d. selesai]
   - Unit/lokasi sampel     : [daftar]
   - Aspek 3E yang diuji    : [Efektivitas / Efisiensi / keduanya]
   - Batasan audit          : [eksplisit — apa yang TIDAK diaudit]

8. HIPOTESIS AUDIT AWAL
   Per sasaran hasil penajaman:
     Sasaran 1: [hipotesis dugaan temuan + data pendukung awal]
     Sasaran 2: [hipotesis dugaan temuan + data pendukung awal]
     ...

9. DOKUMEN YANG MASIH DIBUTUHKAN UNTUK TASK 03
   [daftar dokumen tambahan yang harus diminta sebelum KKP]

                                    Jakarta, [tanggal]

Disusun oleh:                       Disetujui oleh:

Ketua Tim,                          Pengendali Teknis,


[Nama Ketua Tim]                    [Nama Pengendali Teknis]
```

### Update `context.md` setelah SP dibuat
Tambahkan field berikut di `context.md`:
```
Memo Survey Pendahuluan : _SP/SP-[nomor-ST].docx
Sasaran Penajaman       :
  1. [sasaran hasil penajaman]
  2. [sasaran hasil penajaman]
Ruang Lingkup Terukur   : [ringkas dari Memo SP bagian 6]
Hipotesis Audit Awal    : [daftar singkat per sasaran]
```

### GATE 1 — Persetujuan Memo SP sebelum KP + PKP

Sampaikan kepada auditor:
```
=== MEMO SURVEY PENDAHULUAN SELESAI ===

File dibuat: _SP/SP-[nomor-ST].docx

Ringkasan:
  - Area fokus terpilih ([n]): [daftar singkat]
  - Penajaman sasaran: [n] sasaran dari ST → [m] sasaran hasil penajaman
  - Aspek 3E yang diuji: [Efektivitas/Efisiensi/keduanya]
  - Hipotesis audit awal: [ringkas]

Mohon buka Memo SP dan konfirmasi:
  [  ] Hasil research online (Bagian 2) — sumber otoritatif, sitasi URL + tanggal lengkap, relevansi dengan program tepat?
  [  ] Pemetaan risiko sudah menggambarkan kondisi riil program?
  [  ] Area fokus yang dipilih sudah tepat?
  [  ] Sasaran hasil penajaman disetujui untuk menjadi basis KP + PKP?
  [  ] Ruang lingkup sudah realistis untuk periode audit?

Ketik LANJUT untuk generate KP + PKP berdasarkan Memo SP.
Ketik KOREKSI [bagian] jika perlu revisi Memo SP.
```

**JANGAN lanjut ke Bagian A (KP) sebelum auditor menyetujui Memo SP.**

### Aturan Turunan untuk KP + PKP Audit Kinerja
Setelah Memo SP disetujui:
- **Sasaran di KP (field 5)** → gunakan sasaran hasil penajaman dari Memo SP bagian 6, BUKAN verbatim dari ST
- **Ruang Lingkup di KP (field 6)** → gunakan ruang lingkup terukur dari Memo SP bagian 7
- **Langkah Kerja di PKP per sasaran** → turunkan dari hipotesis audit awal (Memo SP bagian 8)
- Cantumkan referensi di KP: *"Sasaran dan ruang lingkup mengacu pada Memo Survey Pendahuluan Nomor [SP/...]"*

---

## BAGIAN A — KARTU PENUGASAN (KP)

### Format Nomor KP
```
KP/[nomor-penugasan]/IJ.3/KP.01.06/[bulan]/[tahun]
Contoh: KP/254/IJ.3/KP.01.06/11/2025
```
Nomor penugasan = nomor urut ST (ambil dari nomor ST).

### Isi Kartu Penugasan

Buat dokumen Word berisi tabel dengan 8 baris berikut. **Semua data diambil dari ST — jangan mengarang.**

| No | Field | Cara Mengisi |
|----|-------|-------------|
| 1 | **Judul Pengawasan** | Salin verbatim dari judul ST |
| 2 | **Dasar Pengawasan** | Nomor dan tanggal ND/PKPT yang menjadi dasar penugasan |
| 3 | **Tingkat Risiko Unit/Aktivitas** | Dari ST atau tanya auditor: Tinggi / Sedang / Rendah |
| 4 | **Tujuan Pengawasan** | Salin dari ST — jika tidak ada, gunakan tujuan standar dari SKILL.md |
| 5 | **Sasaran Pengawasan** | Salin dari ST — numbered list per sasaran |
| 6 | **Ruang Lingkup Pengawasan** | Salin dari ST atau ringkas cakupan berdasarkan sasaran |
| 7 | **Tim** | a. Nama Pengendali Mutu, b. Nama Pengendali Teknis, c. Nama Ketua Tim, d. Nama Anggota Tim (masing-masing baris terpisah) |
| 8 | **Tanggal Pengawasan** | [Tanggal mulai] – [Tanggal selesai] dari ST |

#### Format dokumen KP:

```
                    KARTU PENUGASAN
              KP/[nomor]/IJ.3/KP.01.06/[bulan]/[tahun]

[TABEL 2 KOLOM: No + Field | Isi]

                              Jakarta, [tanggal ST]
                              Disusun Oleh:

                              Pengendali Teknis,


                              [Nama Pengendali Teknis]
```

#### Format Word:
- Tabel 2 kolom: kolom kiri (No + nama field, lebar ±35%), kolom kanan (isi, lebar ±65%)
- Header KP di tengah, bold
- Judul nomor KP di bawahnya, tengah
- Garis tabel solid, semua border
- Font: Times New Roman 12pt atau Arial 11pt
- Blok TTD di kanan bawah, dengan baris kosong untuk tanda tangan

---

## BAGIAN B — PROGRAM KERJA PENGAWASAN (PKP)

### Format Nomor PKP
```
PKP/[nomor-penugasan]/IJ.3/KP.01.06/[bulan]/[tahun]
Contoh: PKP/254/IJ.3/KP.01.06/11/2025
```

### Struktur PKP

PKP berisi **tabel 4 kolom**: Langkah Kerja | Dilaksanakan Oleh | Waktu | KKP No.

PKP dibagi menjadi 3 fase:

#### FASE I — PERENCANAAN
| Langkah Kerja | Dilaksanakan Oleh | Waktu | KKP No. |
|---|---|---|---|
| Susun Program Kerja Pengawasan | [Ketua Tim] | [Tanggal mulai ST] | — |

#### FASE II — PELAKSANAAN
Per sasaran pengawasan (dari ST), buat satu blok. Format per sasaran:

```
Sasaran:
[Nomor]. [Teks sasaran — salin dari ST verbatim]

Langkah Kerja:
a. [Langkah kerja spesifik pertama]
b. [Langkah kerja spesifik kedua]
c. [Langkah kerja spesifik ketiga]
```

Kolom: Dilaksanakan Oleh = [Nama anggota yang bertanggung jawab dari ST] | Waktu = [deadline pelaksanaan] | KKP No. = KKP-[nomor sasaran]/[nomor-penugasan]/IJ.3/KP.01.06/[bulan]/[tahun]

**Cara menyusun Langkah Kerja per sasaran:**
- Langkah kerja harus **spesifik terhadap sasaran** — bukan generik
- Untuk sasaran pengadaan: dapatkan dari SKILL.md steps (bandingkan dokumen, konfirmasi dengan stakeholder, simpulkan)
- Untuk sasaran keuangan: dapatkan data tagihan/pembayaran, bandingkan dengan output/SLA, konfirmasi, simpulkan
- Setiap sasaran minimal 3 langkah: (a) kumpulkan/bandingkan data, (b) konfirmasi/klarifikasi, (c) simpulkan dan tuangkan dalam KKP
- Sesuaikan dengan sasaran nyata dari ST — jangan generik

#### FASE III — PELAPORAN
| Langkah Kerja | Dilaksanakan Oleh | Waktu | KKP No. |
|---|---|---|---|
| Susun Laporan Hasil Pengawasan dan komunikasikan ke satuan kerja terkait | [Ketua Tim] | [Deadline LHP dari ST] | — |

### Header dan Footer PKP

**Header dokumen:**
```
                PROGRAM KERJA PENGAWASAN
          PKP/[nomor]/IJ.3/KP.01.06/[bulan]/[tahun]

A. Judul Pengawasan:
[Judul dari ST]

B. Tujuan Pengawasan:
[Tujuan dari ST]
```

**Blok TTD (2 kolom):**
```
Jakarta, [tanggal ST]            Jakarta, [tanggal ST]
Disetujui Oleh:                  Disusun Oleh:

Pengendali Teknis,               Ketua Tim,



[Nama Pengendali Teknis]         [Nama Ketua Tim]
```

---

## BAGIAN C — TEMPLATE STANDAR UNTUK 6 JENIS PENGAWASAN (Jalur B)

> **Trigger:** Jika `Skill` di `context.md` termasuk salah satu dari 6 jenis terstandar:
> `reviu-rka-kl`, `pemantauan-pengadaan`, `evaluasi-sakip`, `evaluasi-spip`, `evaluasi-reformasi-birokrasi`, `evaluasi-manajemen-risiko`.
>
> Gunakan bagian ini **sebagai pengganti** BAGIAN A-PRE / A / B. KP dan PKP dibuat dengan **find-replace placeholder** pada template `.docx` yang sudah disiapkan.

### C.1 Peta Template per Jenis

Lokasi root: `templates/kp-pkp/[jenis]/`

| Skill | KP Template | PKP Template |
|-------|-------------|--------------|
| `reviu-rka-kl` | `templates/kp-pkp/reviu-rka-kl/KP-template.docx` | `templates/kp-pkp/reviu-rka-kl/PKP-template.docx` |
| `pemantauan-pengadaan` | `templates/kp-pkp/pemantauan-pengadaan/KP-template.docx` | `templates/kp-pkp/pemantauan-pengadaan/PKP-template.docx` |
| `evaluasi-sakip` | `templates/kp-pkp/evaluasi-sakip/KP-template.docx` | `templates/kp-pkp/evaluasi-sakip/PKP-template.docx` |
| `evaluasi-spip` | `templates/kp-pkp/evaluasi-spip/KP-template.docx` | `templates/kp-pkp/evaluasi-spip/PKP-template.docx` |
| `evaluasi-reformasi-birokrasi` | `templates/kp-pkp/evaluasi-reformasi-birokrasi/KP-template.docx` | `templates/kp-pkp/evaluasi-reformasi-birokrasi/PKP-template.docx` |
| `evaluasi-manajemen-risiko` | `templates/kp-pkp/evaluasi-manajemen-risiko/KP-template.docx` | `templates/kp-pkp/evaluasi-manajemen-risiko/PKP-template.docx` |

### C.2 Daftar Placeholder (sama untuk semua 6 jenis)

#### Placeholder identitas penugasan
| Placeholder | Sumber | Contoh |
|-------------|--------|--------|
| `{{OBJEK}}` | ST → judul / objek pengawasan | "Direktorat Jenderal Aplikasi Informatika" |
| `{{TAHUN}}` | ST → tahun penugasan | "2026" |
| `{{TGL_MULAI}}` | ST → tanggal mulai | "15 April 2026" |
| `{{TGL_SELESAI}}` | ST → tanggal selesai | "5 Mei 2026" |
| `{{JUMLAH_HARI}}` | Hitung dari TGL_MULAI–TGL_SELESAI (hari kalender kerja) | "15 hari kerja" |
| `{{NOMOR_ST}}` | ST → nomor surat tugas | "ST/254/IJ.3/KP.01.06/04/2026" |
| `{{TGL_ST}}` | ST → tanggal surat tugas | "14 April 2026" |
| `{{TINGKAT_RISIKO}}` | ST / auditor (Tinggi/Sedang/Rendah) — jika kosong, tulis `[DIISI AUDITOR]` | "Sedang" |
| `{{CATATAN_PENUGASAN}}` | Opsional — catatan khusus di KP. Jika tidak ada → kosongkan / hapus baris | "—" |
| `{{CATATAN_PKP}}` | Opsional — catatan khusus di PKP. Jika tidak ada → kosongkan / hapus baris | "—" |

#### Placeholder tim (dari ST)
| Placeholder | Arti |
|-------------|------|
| `{{PM_NAMA}}`, `{{PM_NIP}}`, `{{PM_JABFUNG}}` | Pengendali Mutu (Inspektur) |
| `{{PT_NAMA}}`, `{{PT_NIP}}`, `{{PT_JABFUNG}}` | Pengendali Teknis |
| `{{KT_NAMA}}`, `{{KT_NIP}}`, `{{KT_JABFUNG}}` | Ketua Tim |
| `{{AT1_NAMA}}`, `{{AT1_NIP}}`, `{{AT1_JABFUNG}}` | Anggota Tim 1 |
| `{{AT2_NAMA}}`, `{{AT2_NIP}}`, `{{AT2_JABFUNG}}` | Anggota Tim 2 (jika tim hanya 4 orang → isi `-`) |
| `{{INSPEKTUR_NAMA}}`, `{{INSPEKTUR_NIP}}` | Penandatangan KP (umumnya = PM) |

#### Placeholder alokasi waktu PKP
| Placeholder | Arti |
|-------------|------|
| `{{HK_PERSIAPAN}}` | Jumlah hari kerja tahap persiapan (default 2) |
| `{{HK_PELAKSANAAN}}` | Jumlah hari kerja tahap pelaksanaan (default JUMLAH_HARI − persiapan − pelaporan) |
| `{{HK_PELAPORAN}}` | Jumlah hari kerja tahap pelaporan (default 3) |

#### Placeholder khusus (hanya untuk jenis tertentu)
| Placeholder | Skill yang pakai | Keterangan |
|-------------|------------------|------------|
| `{{TRIWULAN}}` | `evaluasi-reformasi-birokrasi` | Diisi "I", "II", "III", atau "IV" sesuai periode evaluasi on-going |

### C.3 Prosedur Eksekusi (Jalur B)

1. **Baca `context.md`** — ambil: Skill, Objek, Tahun, Nomor ST, Tanggal ST, Periode Pengawasan, Tim (PM/PT/KT/AT), Tingkat Risiko (jika ada).
2. **Tentukan folder template** berdasarkan Skill (tabel C.1).
3. **Hitung placeholder turunan**:
   - `{{JUMLAH_HARI}}` = jumlah hari kerja antara TGL_MULAI dan TGL_SELESAI (asumsi 5 hari kerja/minggu kecuali disebutkan lain di ST).
   - `{{HK_PERSIAPAN}}` / `{{HK_PELAKSANAAN}}` / `{{HK_PELAPORAN}}` — default 2 / sisa / 3. Jika auditor punya preferensi, minta konfirmasi.
   - `{{TRIWULAN}}` — hanya untuk `evaluasi-reformasi-birokrasi`; tanyakan auditor bila belum jelas dari ST.
4. **Unpack template KP** ke folder sementara (gunakan `scripts/office/unpack.py` dari skill `docx`).
5. **Find-replace** seluruh placeholder `{{...}}` di `word/document.xml` (dan `word/header*.xml` bila ada) dengan nilai yang telah ditentukan. Untuk field yang tidak tersedia di ST → **tulis `[DIISI AUDITOR]`**, jangan mengarang.
6. **Pack** kembali menjadi `.docx` (gunakan `scripts/office/pack.py`) dan **validate**.
7. **Simpan** hasil ke:
   - `_KP/KP-[nomor-ST].docx`
   - `_PKP/PKP-[nomor-ST].docx`
8. **Ulangi langkah 4–7** untuk PKP-template.docx.
9. **Update `context.md`** (lihat Langkah 4 di LANGKAH EKSEKUSI di bawah).
10. **Konfirmasi ke auditor** — gunakan blok konfirmasi pada Langkah 5.

### C.4 Aturan Penting Jalur B

- **Jangan ubah struktur template** (tabel, heading, urutan bagian). Template sudah disesuaikan dengan regulasi setiap jenis; perubahan struktur = merusak standarisasi.
- **Hanya ganti placeholder** `{{...}}` — baris lain biarkan apa adanya.
- **Jika ST mengandung penajaman sasaran / ruang lingkup yang berbeda dari template**: catat di `{{CATATAN_PENUGASAN}}` (untuk KP) dan `{{CATATAN_PKP}}` (untuk PKP), **jangan** rewrite langkah kerja.
- **Jumlah hari** di PKP harus konsisten dengan `{{JUMLAH_HARI}}` di KP. Jika jumlah langkah kerja > hari tersedia → catat di `{{CATATAN_PKP}}`, minta auditor menyesuaikan beban kerja.
- **Jika auditor meminta perubahan substansial** (tambah/ubah langkah kerja, ubah tujuan, ubah sasaran) → lakukan **setelah** template diisi, sebagai edit manual di atas output; dan minta auditor konfirmasi bahwa perubahan ini memang diperlukan untuk penugasan ini (bukan sistemik — jika sistemik, usulkan update template dulu).

---

## LANGKAH EKSEKUSI

### 1. Muat konteks
Baca `context.md`. Pastikan Tim, Tujuan, Sasaran, Nomor ST, dan Periode sudah lengkap.

### 1.5. Tentukan JALUR
Baca field `Skill :` di `context.md`:
- `audit-kinerja` / `audit-pengadaan` / `reviu-pengadaan` / `konsultasi-pengadaan` → **Jalur A (Bespoke)** → lanjut Langkah 2A / 2B / 3.
- `reviu-rka-kl` / `pemantauan-pengadaan` / `evaluasi-sakip` / `evaluasi-spip` / `evaluasi-reformasi-birokrasi` / `evaluasi-manajemen-risiko` → **Jalur B (Template Standar)** → **LOMPAT ke Langkah 2C**.

**Cek skill yang aktif (khusus Jalur A):**
- Jika `Skill = audit-kinerja` (atau sub-skill `audit-kinerja-[program]`) → **wajib** jalankan Langkah 2A (Survey Pendahuluan) terlebih dahulu
- Jika skill Jalur A lain (audit-pengadaan, reviu-pengadaan, konsultasi-pengadaan) → lewati Langkah 2A, langsung ke Langkah 2B

### 2A. Generate Memo Survey Pendahuluan (WAJIB untuk audit-kinerja)
- Pastikan dokumen program (proses bisnis, PK, LKj, DIPA, TOR/KAK, data realisasi) sudah tersedia. Jika belum → minta auditor upload terlebih dahulu.
- Ikuti langkah pelaksanaan pada **BAGIAN A-PRE** di atas.
- Buat file Word: `_SP/SP-[nomor-ST].docx`.
- Update `context.md` dengan field: Memo Survey Pendahuluan, Sasaran Penajaman, Ruang Lingkup Terukur, Hipotesis Audit Awal.
- **GATE 1**: minta konfirmasi auditor atas Memo SP sebelum lanjut ke Langkah 2B.
- Jika auditor meminta koreksi → revisi Memo SP, minta konfirmasi ulang.

### 2B. Generate KP
- Buat file Word: `_KP/KP-[nomor-ST].docx`
- Isi semua 8 field:
  - **Untuk audit-kinerja**: field 5 (Sasaran) dan field 6 (Ruang Lingkup) **DIAMBIL DARI MEMO SP** (sasaran hasil penajaman + ruang lingkup terukur), BUKAN verbatim dari ST. Cantumkan catatan di bawah tabel: *"Sasaran dan ruang lingkup mengacu pada Memo Survey Pendahuluan Nomor [SP/...]"*.
  - **Untuk skill lain**: isi dari data ST seperti biasa.
- Jika ada field yang tidak ada di ST (misal Tingkat Risiko): **tandai `[DIISI AUDITOR]`** — jangan mengarang.

### 3. Generate PKP
- Buat file Word: `_PKP/PKP-[nomor-ST].docx`
- Fase I dan III: template standar (isi nama tim dan tanggal)
- Fase II: satu blok per sasaran, dengan langkah kerja yang relevan
  - **Untuk audit-kinerja**: sasaran diambil dari Memo SP (sasaran hasil penajaman). Langkah kerja per sasaran **diturunkan dari Hipotesis Audit Awal (Memo SP bagian 7)** — setiap hipotesis menjadi dasar satu atau lebih langkah pengujian.
  - **Untuk skill lain (Jalur A)**: sasaran dari ST; langkah kerja dari SKILL.md/references sesuai konteks sasaran.
- Setiap blok sasaran: langkah kerja berbeda sesuai konteks sasaran (tidak boleh copy-paste)
- KKP No. per sasaran: format `KKP-[n]/[nomor-ST]/IJ.3/KP.01.06/[bulan]/[tahun]`

### 2C. Generate KP + PKP dari Template Standar (JALUR B)
- Ikuti **BAGIAN C.3 Prosedur Eksekusi** di atas.
- Output:
  - `_KP/KP-[nomor-ST].docx`
  - `_PKP/PKP-[nomor-ST].docx`
- **Semua placeholder `{{...}}` harus terisi** — field yang tidak tersedia di ST ditandai `[DIISI AUDITOR]`.
- **Tidak perlu Memo SP** untuk jalur B (kecuali auditor secara eksplisit memintanya).
- Setelah selesai, lanjut ke **Langkah 4** (Update context.md) dan **Langkah 5** (Konfirmasi).

### 4. Update context.md
```
Status  : TAHAP 1 — MENUNGGU KONFIRMASI KP + PKP
File SP : _SP/SP-[nomor-ST].docx       (jika audit-kinerja)
File KP : _KP/KP-[nomor-ST].docx
File PKP: _PKP/PKP-[nomor-ST].docx
```

### 5. Konfirmasi kepada auditor

```
=== KP + PKP SELESAI ===

File yang dibuat:
  1. _KP/KP-[nomor-ST].docx   ← Kartu Penugasan
  2. _PKP/PKP-[nomor-ST].docx ← Program Kerja Pengawasan

Ringkasan PKP:
  - [N] sasaran pengawasan
  - Sasaran 1: [judul singkat] → Pelaksana: [nama] → Deadline: [tanggal]
  - Sasaran 2: [judul singkat] → Pelaksana: [nama] → Deadline: [tanggal]
  [dst...]
  - Pelaporan: [Ketua Tim] → [deadline]

Field yang perlu dicek auditor sebelum finalisasi:
  [  ] Tingkat Risiko Unit/Aktivitas → saat ini: [nilai atau "DIISI AUDITOR"]
  [  ] Langkah kerja per sasaran → apakah sudah tepat?
  [  ] Pembagian pelaksana per sasaran → apakah sudah sesuai?

Mohon buka kedua file dan:
  1. Koreksi jika ada yang tidak tepat (balas di chat)
  2. Isi field yang masih kosong/placeholder langsung di Word

Setelah KP + PKP disetujui, ketik LANJUT untuk memulai Task 03 (analisis dokumen dan KKP).
```

---

## Output
- `_SP/SP-[nomor-ST].docx` — Memo Survey Pendahuluan **(wajib untuk audit-kinerja)**
- `_KP/KP-[nomor-ST].docx` — Kartu Penugasan
- `_PKP/PKP-[nomor-ST].docx` — Program Kerja Pengawasan
- `context.md` diperbarui

## ⛔ GATE — Jangan lanjutkan ke Task 03 sebelum:
1. **(audit-kinerja)** Auditor menyetujui Memo SP — Sasaran dan ruang lingkup hasil penajaman disetujui
2. Auditor sudah membuka dan membaca KP + PKP
3. Auditor memberikan konfirmasi via chat (minimal "OK lanjut" atau koreksi spesifik)
4. Jika ada koreksi → perbaiki file Word, minta konfirmasi ulang

## Aturan Anti-Halusinasi

### Untuk Memo Survey Pendahuluan (audit-kinerja)
- **Data realisasi dan target HARUS dari dokumen** — PK, LKj, e-monev, DIPA; jangan estimasi
- **Setiap risiko teridentifikasi** harus punya bukti/indikasi dari data (bukan spekulasi)
- **Penajaman sasaran** harus dapat dijustifikasi berbasis area fokus — bukan karangan
- **Hipotesis audit awal** bukan kesimpulan — tandai eksplisit sebagai *"dugaan yang akan diuji di Task 03"*
- Jika dokumen program tidak lengkap → nyatakan sebagai keterbatasan di Memo SP dan minta auditor sediakan sebelum lanjut ke PKP

### Untuk Research Online (Bagian 2 Memo SP)
- **Setiap baris tabel Bagian 2 WAJIB** memuat URL lengkap + tanggal akses (hari ini) + nama sumber lengkap. Tidak boleh kosong — jika tidak ada, tandai `[DIISI AUDITOR]`.
- **Jangan parafrasa angka tanpa sumber** — jika mengutip angka dari laporan K/L lain / best practice, cantumkan halaman/bagian.
- **Sumber harus otoritatif** (`.go.id`, bpk.go.id, bpkp.go.id, oecd.org, worldbank.org, intosai.org, jurnal akademis) — tolak blog/SEO farm/media sosial.
- **Jika sumber tidak bisa diakses penuh** (paywall, 403, PDF rusak) → jangan pakai snippet sebagai klaim; tandai *"perlu verifikasi auditor"*.
- **Jika salah satu dari 4 jenis research tidak menghasilkan sumber memadai** → isi Bagian 2.5 dengan pernyataan eksplisit, jangan kosongkan.
- **Research online BUKAN kriteria utama** untuk temuan audit — hanya konteks pembanding. Kriteria utama tetap dari proses bisnis/SOP/PK program yang diaudit.

### Untuk KP dan PKP
- **Untuk audit-kinerja**: Sasaran dan Ruang Lingkup wajib dari Memo SP (hasil penajaman), bukan verbatim dari ST
- **Untuk skill lain**: Judul, Tujuan, Sasaran, Tim, Periode wajib salin dari ST
- **Jangan mengarang sasaran** yang tidak ada di ST atau Memo SP
- **Jangan mengarang nama** anggota tim — hanya yang ada di ST
- **Jangan mengarang langkah kerja** yang tidak relevan dengan sasaran/hipotesis
- Jika ada informasi yang tidak tersedia: tandai `[DIISI AUDITOR]`
- Jika ada perbedaan antara ST dan dokumen lain: gunakan ST sebagai referensi utama

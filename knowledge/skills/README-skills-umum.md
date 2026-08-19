# 5 Skill Umum (Generic, Criteria-Driven) — audit-system-v4

**Versi:** 1.0 (Mei 2026)
**Lokasi:** `audit-system-v4/skills/{audit,reviu,pemantauan,evaluasi,konsultansi}-umum/`

## Ringkasan

5 skill umum melengkapi keluarga skill spesifik di audit-system-v4. Skill umum dipakai ketika **belum ada skill khusus** untuk objek pengawasan, dan kriteria pengujian akan diunggah auditor di `input/kriteria/` saat penugasan dimulai.

| Skill | Fungsi APIP | Tingkat Keyakinan | Output Utama | Kode Surat |
|-------|-------------|-------------------|--------------|------------|
| **audit-umum** | Assurance | Memadai | LHA + KKA | PW.04.04 |
| **reviu-umum** | Assurance | Terbatas | LHR + KKR | PW.04.04 |
| **pemantauan-umum** | Assurance | Status/Progres | LHPemantauan + KKM | PW.04.06 |
| **evaluasi-umum** | Assurance | Penilaian Substantif | LHE + KKE | PW.04.05 |
| **konsultansi-umum** | Consulting | (tanpa keyakinan) | Memo Konsultasi | menyesuaikan |

## Kapan Pakai Skill Umum vs Spesifik

**Pakai skill spesifik** jika tersedia (lebih lengkap, sudah punya checklist, references built-in):

| Topik | Skill Spesifik |
|-------|----------------|
| Pengadaan Barang/Jasa | `audit-pengadaan`, `reviu-pengadaan`, `pemantauan-pengadaan`, `konsultasi-pengadaan` |
| RKA-K/L | `reviu-rka-kl` |
| Kinerja / SAKIP | `audit-kinerja`, `evaluasi-sakip` |
| SPIP / Manajemen Risiko | `evaluasi-spip`, `evaluasi-manajemen-risiko` |
| Reformasi Birokrasi | `evaluasi-reformasi-birokrasi` |
| Tindak Lanjut Hasil Pengawasan | `pemantauan-tindak-lanjut` |
| Kepatuhan SAIPI | `kepatuhan-saipi` |

**Pakai skill umum** ketika:
- Tidak ada skill spesifik untuk objek pengawasan
- Penugasan strategis dengan kriteria ad-hoc
- Penugasan kombinasi (sebagian sudah ada skill, sebagian belum)
- Eksperimen/ujicoba kriteria baru sebelum dijadikan skill spesifik

## Decision Tree

```
Mulai penugasan baru
│
├── Ada skill spesifik untuk topik ini? ──── YA ──> Pakai skill spesifik
│                                              
└── TIDAK
    │
    ├── Tujuan: keyakinan memadai + analisis akar masalah?  ──> audit-umum
    ├── Tujuan: keyakinan terbatas + administratif?         ──> reviu-umum
    ├── Tujuan: laporan status/progres terhadap target?     ──> pemantauan-umum
    ├── Tujuan: penilaian efektivitas/skor/predikat?        ──> evaluasi-umum
    └── Tujuan: jawaban tertulis atas pertanyaan unit?      ──> konsultansi-umum
```

## Struktur Folder per Skill

```
audit-system-v4/skills/[skill-umum]/
├── SKILL.md                                     # Definisi skill
└── references/
    ├── 01-panduan-ekstraksi-kriteria.md         # Auto-detect kriteria (sama di 5 skill)
    └── [02-...]                                 # Khusus per skill (mis. checklist bukti, bahasa keyakinan)
```

## Struktur Folder Penugasan (template)

```
audit-system-v4/penugasan/[ID-PENUGASAN]/
├── 00-surat-tugas/        # ST + ND permintaan
├── input/
│   ├── kriteria/          # ← Auditor unggah PDF/DOCX/XLSX/TXT regulasi/SOP/juklak
│   ├── objek/             # ← Dokumen objek pengawasan
│   ├── pertanyaan/        # ← Khusus konsultansi-umum
│   └── data-pendukung/
├── _KKP/                  # Output Claude (xlsx + json + audit trail)
└── _LHP/                  # Output Claude (docx final)
```

## Pola Workflow Bersama (Gate-Based)

Semua 5 skill mengikuti pola gate yang sama:

```
Gate 0: Validasi Input
   ↓ STOP — auditor konfirmasi kelengkapan
Gate 1: Kerangka Penugasan (KP)
   ↓ STOP — auditor konfirmasi KP
Gate 2: Program Kerja Pengujian (PKP)
   ↓ STOP — auditor konfirmasi PKP
Gate 3: Pelaksanaan & Kertas Kerja (KKA/KKR/KKM/KKE/KKK)
   ↓ STOP — auditor konfirmasi temuan/catatan material
Gate 4: Laporan (LHA/LHR/LHPemantauan/LHE/Memo) + Nota Dinas
   ↓ STOP — review final sebelum penomoran
```

Mengikuti prinsip gate-based wajib (lihat memory `feedback_gate_based_workflow`).

## Output JSON KKP — Skema Bersama

Setiap skill menghasilkan `_KKP/temuan.json` dengan field minimum:

```json
{
  "penugasan_id": "string",
  "skill": "audit-umum|reviu-umum|...",
  "version": "1.0",
  "kriteria_terindeks": [
    {"id": "K01", "sumber": "...", "pasal": "...", "kutipan": "...", "level": "L1-L9"}
  ],
  "audit_trail": [
    {"timestamp": "ISO-8601", "tindakan": "...", "file": "...", "auditor": "..."}
  ]
}
```

Field tambahan per skill (`temuan` untuk audit/evaluasi, `catatan_reviu` untuk reviu, `items` untuk pemantauan, `pendapat` untuk konsultansi).

## Format Output Surat Dinas — Bersama

Semua 5 skill memakai format **Nota Dinas Pengantar + Laporan/Memo format surat dinas** sesuai `audit-system-v4/skills/panduan-format-umum/PANDUAN.md`.

Bahasa simpulan per fungsi:
- **Audit (memadai):** "berdasarkan audit yang dilakukan sesuai standar..."
- **Reviu (terbatas):** "tidak terdapat hal-hal yang membuat kami yakin bahwa... tidak terpenuhi"
- **Pemantauan:** "berdasarkan pemantauan periode X, [N] item berstatus hijau, ..."
- **Evaluasi (penilaian):** "berdasarkan hasil evaluasi, [objek] memperoleh nilai X dengan predikat Y"
- **Konsultansi (tanpa keyakinan):** "berdasarkan penelaahan kami, kami berpendapat bahwa..."

## Graduasi ke Skill Spesifik

Setelah skill umum dipakai untuk penugasan, **pola yang muncul** (kriteria yang dipakai, red flag yang ditemukan, format laporan yang sudah disetujui) dapat digraduasi otomatis menjadi **skill spesifik baru** lewat meta-skill `graduasi-skill-spesifik`.

### Trigger
**Manual, mode batch (Recommended: Jumat sore mingguan).** Graduasi dipisahkan dari workflow penugasan agar penugasan tetap cepat. Auditor jalankan sesi batch terpisah:

```bash
# Step 1 — scan kandidat (Jumat sore):
python audit-system-v4/skills/graduasi-skill-spesifik/scripts/graduasi.py \
    --root audit-system-v4 --candidates --only-unscheduled

# Step 2 — graduate cluster yang siap (≥3 penugasan domain mirip):
python audit-system-v4/skills/graduasi-skill-spesifik/scripts/graduasi.py \
    --root audit-system-v4 \
    --penugasan ID1 ID2 ID3 \
    --nama [fungsi]-[topik]
```

Atau berdialog dengan Claude pada sesi batch:
> "Sekarang sesi batch Jumat. Tolong scan kandidat graduasi dulu."

**Catatan:** graduasi **dipisah dari workflow penugasan** agar penugasan tetap cepat. Skill di `_draft/` dapat di-review/promote di sesi batch berikutnya, tidak harus di sesi yang sama.

### Tingkat Graduasi

| Jumlah Penugasan | Tingkat | Output |
|---|---|---|
| 1 penugasan | Minimum | SKILL.md + references core + checklist (catatan: observasi tunggal) |
| 2–4 penugasan | Standar | + regulasi pendukung + red flag konsolidasi |
| ≥5 penugasan | Penuh | + pipeline script Python (digest.py + cross_check.py skeleton) |

### Lifecycle Draft → Aktif

```
Penugasan dengan skill umum
        ↓ graduasi-skill --penugasan ...
skills/_draft/<nama-skill>/         ← status: draft-pending-approval
        ↓ auditor review
        ├── promote → skills/<nama-skill>/   (aktif, version 1.0)
        └── reject  → folder dihapus
```

Detail lifecycle dan aturan review: `audit-system-v4/skills/_draft/README.md`.

### Kapan Sebaiknya Graduasi

- ✅ Topik sudah berulang (≥3 penugasan dengan pola mirip)
- ✅ Kriteria sudah stabil (tidak banyak perubahan regulasi)
- ✅ Ada pola checklist/red flag yang konsisten
- ✅ Tim sudah punya benchmark output

### Kapan Tunda Graduasi

- ❌ Topik baru sekali muncul tanpa indikasi akan berulang
- ❌ Kriteria masih berubah-ubah (regulasi sedang revisi)
- ❌ Pola temuan masih sangat bervariasi antar penugasan
- ❌ Tim belum sepakat tentang format laporan

## Verifikasi & Konsistensi

- ✅ Format Nota Dinas + surat dinas konsisten dengan `panduan-format-umum/PANDUAN.md`
- ✅ Matriks elemen isi laporan (Kondisi/Kriteria/Sebab/Akibat/Rekomendasi) sesuai jenis pengawasan
- ✅ Bahasa keyakinan sesuai tingkat
- ✅ Auto-detect kriteria mengikuti `01-panduan-ekstraksi-kriteria.md`
- ✅ Gate-based — tidak boleh skip gate (lihat feedback memory)

## Decision Tree Lengkap (5 Skill Umum + Meta-Skill)

```
Mulai penugasan baru
│
├── Ada skill spesifik? ──── YA ──> Pakai skill spesifik
│
└── TIDAK
    │
    ├── audit-umum / reviu-umum / pemantauan-umum / evaluasi-umum / konsultansi-umum
    │       ↓
    │   selesai Gate 4
    │       ↓
    └── Sudah selesai ≥1 penugasan dengan pola mirip?
            ↓
            graduasi-skill-spesifik (manual trigger)
                ↓
            skills/_draft/<nama-skill>/
                ↓
            auditor review → promote / reject
```

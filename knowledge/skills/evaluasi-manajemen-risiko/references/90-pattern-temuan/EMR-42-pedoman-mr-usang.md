<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-manajemen-risiko/EMR-42-pedoman-mr-usang.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: EMR-42
skill: evaluasi-manajemen-risiko
kategori: MR-PEDOMAN
severity: HIGH
judul: "Pedoman MR Usang / Belum Disesuaikan SOTK & Praktik Terkini"
kriteria_baku: "Permenkominfo 6/2017 (usang) vs SOTK PM Komdigi 1/2025 + Three Lines Model"
tags: [mr, pedoman-usang, permenkominfo-6-2017, sotk, three-lines-model, evaluasi-mr]
---

# EMR-42: Pedoman MR Usang / Belum Disesuaikan SOTK

## Pattern Kondisi

Pedoman Manajemen Risiko masih merujuk regulasi lama dan belum disesuaikan dengan SOTK/praktik MR terkini. Indikator umum:

- Pedoman MR masih Permenkominfo 6/2017 (pra-SOTK Komdigi)
- Three Lines Model (IIA 2020) belum diimplementasikan optimal
- Standar kompetensi SDM MR belum ditetapkan
- Belum ada prosedur identifikasi & pelaporan insiden risiko
- SIMR belum punya fitur *early warning* + belum terintegrasi (lihat EMR-43/sistem)

## Kriteria

Pedoman MR + tata kelola — pedoman wajib dimutakhirkan mengikuti SOTK (PM Komdigi 1/2025) dan kerangka MR modern (Three Lines Model IIA 2020).

## Akibat

1. Kerangka MR tidak selaras struktur organisasi terkini
2. Implementasi MR tidak konsisten antar-unit
3. Maturitas MR tertahan

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Pedoman MR | tanggal + regulasi rujukan |
| SOTK terkini | kesesuaian struktur dengan pedoman |
| Standar kompetensi MR | ada/tidak |
| SOP insiden risiko | ada/tidak |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-EMR-42",
  "assigned_to": "{nama anggota}",
  "judul": "Pedoman MR Masih {regulasi lama} — Belum Disesuaikan SOTK & Praktik Terkini",
  "kondisi": "Pedoman MR {satker} masih merujuk {Permenkominfo 6/2017}; belum disesuaikan SOTK PM Komdigi 1/2025. Three Lines Model belum optimal; standar kompetensi SDM MR belum ditetapkan; SOP identifikasi/pelaporan insiden risiko belum ada.",
  "kriteria": "Pedoman MR + tata kelola — pedoman wajib dimutakhirkan mengikuti SOTK terkini & kerangka MR modern (Three Lines Model).",
  "akibat": "Kerangka MR tidak selaras struktur terkini; implementasi tidak konsisten; maturitas MR tertahan.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Pedoman MR Permenkominfo 6/2017 ..."}]
}
```

## Contoh Kasus Historis

- **LHE Manajemen Risiko 2026** — pedoman MR masih **Permenkominfo 6/2017** (usang); Three Lines Model belum optimal; standar kompetensi SDM MR belum ditetapkan; SIMR belum *early warning*; belum ada SOP insiden risiko. Lihat [[lhe-manajemen-risiko-2026]], [[pattern-temuan]] P-23.

## Catatan

- Pattern lintas-skill P-23 (Pedoman/SOP Usang) — sama dengan [[kepatuhan-saipi/SAIPI-60-piagam-audit-belum-diperbarui]] (Piagam Audit 757/2018).
- Rekomendasi: revisi pedoman MR dengan jadwal konkret + adopsi Three Lines Model.

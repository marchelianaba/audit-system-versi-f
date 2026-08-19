<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/konsultasi-pengadaan/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Konsultasi Pengadaan

Index pattern temuan yang berlaku untuk skill `konsultasi-pengadaan`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

> Catatan: `konsultasi-pengadaan` adalah aktivitas **consulting/advisory** APIP (SAIPI 2010) — bersifat *pra-pengadaan* (sebelum proses pemilihan). Pattern di sini lebih banyak berupa **titik perhatian advisory** ketimbang temuan audit; severity umumnya MEDIUM/INFO.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| KSP-57 | E-Katalog Tanpa Mini-Kompetisi untuk Nilai Signifikan | PBJ-PEMILIHAN | MEDIUM | Kepka LKPP 93/2025 |
| KSP-58 | Pemaketan/Spesifikasi Belum Jelas Saat Penyusunan HPS | PBJ-HPS | MEDIUM | Perpres 16/2018 Pasal 18 + 26 |
| KSP-59 | Itjen Dilibatkan sebagai Advisor Pra-Pengadaan (Good Practice) | PBJ-ADVISORY | INFO | SAIPI 2010 (consulting activity) |

## Kategori yang dipakai

- `PBJ-PEMILIHAN` — kewajaran metode pemilihan (mini-kompetisi, negosiasi)
- `PBJ-HPS` — kejelasan pemaketan & spesifikasi untuk HPS
- `PBJ-ADVISORY` — peran consulting APIP pra-pengadaan (good practice)

## Sumber data pattern

Pattern di folder ini disusun dari penugasan konsultasi/advisory Inspektorat II TA 2026:

- ST-90 Konsultasi Teknis HPS, Review Final, Pemaketan, Mini-Kompetisi E-Katalog DJED (12-14 Mei 2026, The Luxton Bandung) — lihat [[surat-tugas-ir2-mei-2026]]
- ND-135 LH Monitoring Redesain TKPPSE (rekomendasi mini-kompetisi)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk
- [[reviu-pengadaan/README]] — pattern reviu Pengadaan
- [[pemantauan-pengadaan/PMP-54-selisih-penawaran-tanpa-kompetisi]]

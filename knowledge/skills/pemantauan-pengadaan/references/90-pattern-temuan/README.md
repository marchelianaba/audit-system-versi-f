<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-pengadaan/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Pemantauan Pengadaan

Index pattern temuan yang berlaku untuk skill `pemantauan-pengadaan`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| PMP-53 | Jawaban RFI Belum Lengkap Menghambat Target Pengadaan | PBJ-RFI | HIGH | Perpres 16/2018 Pasal 18 (perencanaan) |
| PMP-54 | Selisih Penawaran Signifikan Tanpa Mekanisme Kompetisi Objektif | PBJ-PEMILIHAN | HIGH | Kepka LKPP 93/2025 (mini-kompetisi e-Katalog) |
| PMP-55 | Pagu SIRUP Status Draft Tinggi Mendekati Pelaksanaan | PBJ-SIRUP | HIGH | Perpres 16/2018 Pasal 22 + Peraturan LKPP RUP |
| PMP-56 | Kajian Selesai Tapi Belum Diturunkan ke Milestone Implementasi | PBJ-PERENCANAAN | MEDIUM | Perpres 16/2018 Pasal 18 |

## Kategori yang dipakai

- `PBJ-RFI` — kelengkapan & progres Request for Information
- `PBJ-PEMILIHAN` — kewajaran metode pemilihan & kompetisi
- `PBJ-SIRUP` — status RUP/SIRUP & kesiapan pelaksanaan
- `PBJ-PERENCANAAN` — turunan kajian ke rencana aksi/milestone
- `PBJ-PROGRES` — pemantauan progres fisik/keuangan pengadaan

## Sumber data pattern

Pattern di folder ini disusun dari LH Monitoring/Pemantauan Pengadaan Inspektorat II TA 2026:

- LH Monitoring Progres Redesain TKPPSE (ND-135, output ST-81) — RFI 2/6 vendor menjawab
- LHP Pengadaan Program Prioritas Wasdig 2026 (SIRUP 68,36% draft per 27 Jan)
- LHP Pengadaan Redesain TKPPSE 2026 (kajian → implementasi)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-19 SIRUP draft, P-31 kajian tanpa milestone)
- [[reviu-pengadaan/README]] — pattern reviu Pengadaan (pre-award)
- [[audit-pengadaan/README]] — pattern audit Pengadaan (post-award)
- [[nota-dinas-ir2-mei-2026]] (ND-135) — LH Monitoring Redesain TKPPSE

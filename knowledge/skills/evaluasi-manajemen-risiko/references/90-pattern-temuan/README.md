<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-manajemen-risiko/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Evaluasi Manajemen Risiko

Index pattern temuan yang berlaku untuk skill `evaluasi-manajemen-risiko`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| EMR-39 | Pemantauan Risiko Triwulanan Belum Diinput | MR-PEMANTAUAN | HIGH | Pedoman MR K/L + komponen pemantauan |
| EMR-40 | Piagam Risiko Belum Ditandatangani/Diunggah | MR-KOMITMEN | HIGH | Pedoman MR + Three Lines Model IIA 2020 |
| EMR-41 | Rencana Penanganan Risiko Belum Diisi (Risiko Strategis) | MR-PENANGANAN | HIGH | Pedoman MR |
| EMR-42 | Pedoman MR Usang / Belum Disesuaikan SOTK | MR-PEDOMAN | HIGH | Permenkominfo 6/2017 (usang) vs SOTK 2025 |
| EMR-43 | Gap Komitmen Top-Down (Pemilik Risiko Tertinggi Belum Lengkap) | MR-TATAKELOLA | CRITICAL | Pedoman MR + Three Lines Model |

## Kategori yang dipakai

- `MR-KONTEKS` — penetapan konteks risiko
- `MR-PROFIL` — profil & peta risiko
- `MR-PENANGANAN` — rencana penanganan/tindak risiko
- `MR-PEMANTAUAN` — pemantauan triwulanan/berkala
- `MR-KOMITMEN` — Piagam Risiko & formalisasi komitmen pimpinan
- `MR-PEDOMAN` — kemutakhiran pedoman/regulasi MR
- `MR-SISTEM` — sistem informasi MR (SIMR, early warning)
- `MR-TATAKELOLA` — Three Lines Model, gap top-down

## Sumber data pattern

Pattern di folder ini disusun dari LHE MR Inspektorat II TA 2026:

- Quartet LHE MR TW I (ND-124 Itjen 93,3% / ND-125 DJPRD 93,3% / ND-126 DJED 60% / ND-127 Menteri 40%) — lihat [[nota-dinas-ir2-april-2026]]
- LHE Manajemen Risiko 2026 (SIMR belum early warning; pedoman PM 6/2017)
- LHE MR Triwulan 1 2026
- Atensi Progres SPIP & MR 2025 (MR DJED/DJPRD/DJTPD 0% pengisian)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-23 pedoman usang, P-28 sistem belum early warning, P-33)
- [[lhe-mr-triwulan-1-2026]] / [[lhe-manajemen-risiko-2026]]
- [[piagam-mr-itjen-2026]] / [[piagam-mr-ir2-2026]] — dokumen MR satker
- [[evaluasi-spip/README]] — MRI bagian dari maturitas SPIP
- [[framework-evaluasi-mr]]

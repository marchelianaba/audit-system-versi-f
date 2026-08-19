<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-sakip/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Evaluasi SAKIP

Index pattern temuan yang berlaku untuk skill `evaluasi-sakip`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| ESK-30 | Stagnasi Predikat AKIP Beberapa Tahun Berturut-turut | SAKIP-HASIL | HIGH | Permenpan-RB 88/2021 |
| ESK-31 | Komponen Pengukuran Kinerja Bernilai Terendah | SAKIP-PENGUKURAN | HIGH | Permenpan-RB 88/2021 (bobot 30%) |
| ESK-32 | Indikator Kinerja Belum SMART / Berorientasi Proses | SAKIP-PERENCANAAN | HIGH | Permenpan-RB 88/2021 + Perpres 29/2014 |
| ESK-33 | Penjenjangan (Cascading) Kinerja Belum Lengkap s.d. Eselon II | SAKIP-CASCADING | MEDIUM | Permenpan-RB 88/2021 |
| ESK-34 | Hasil Pengukuran Belum Dipakai sebagai Decision Tool | SAKIP-PEMANFAATAN | MEDIUM | Permenpan-RB 88/2021 |

## Kategori yang dipakai

- `SAKIP-HASIL` — nilai/predikat akhir AKIP & trennya
- `SAKIP-PERENCANAAN` — kualitas sasaran & indikator (SMART, orientasi hasil) — bobot 30%
- `SAKIP-PENGUKURAN` — kualitas pengukuran kinerja — bobot 30%
- `SAKIP-PELAPORAN` — kualitas pelaporan kinerja — bobot 15%
- `SAKIP-EVALUASI` — evaluasi akuntabilitas internal — bobot 25%
- `SAKIP-CASCADING` — penjenjangan kinerja antar level
- `SAKIP-PEMANFAATAN` — pemanfaatan hasil pengukuran sebagai dasar keputusan

## Sumber data pattern

Pattern di folder ini disusun dari LHE AKIP Inspektorat II + Kemenpan-RB TA 2023–2026:

- LHE AKIP eksternal Kemenpan-RB 2023–2024
- LHE AKIP internal Itjen 2023–2025
- LHE AKIP 2025 Kemkomdigi (B/505/AA.05/2025 — nilai 69,14 predikat B)
- ND-133 Atensi Pengawasan Implementasi SAKIP 2026 (lihat [[nota-dinas-ir2-mei-2026]])

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-33 SPIP/MR/RB stagnan, P-35 data tidak traceable)
- [[lhe-akip-2025-kemkomdigi]] / [[lhe-akip-eksternal-kemenpanrb-2023-2024]] / [[lhe-akip-internal-itjen-2023-2025]]
- [[reviu-rka-kl/RKA-02-ro-tanpa-parameter-keberhasilan]] — indikator SMART di RKA-K/L

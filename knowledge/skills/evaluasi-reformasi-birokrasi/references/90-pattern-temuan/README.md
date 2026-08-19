<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-reformasi-birokrasi/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Evaluasi Reformasi Birokrasi

Index pattern temuan yang berlaku untuk skill `evaluasi-reformasi-birokrasi`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| ERB-44 | Rencana Aksi RB Sesuai Tapi Outcome/Dampak Tidak Diukur | RB-OUTCOME | HIGH | Permenpan-RB 3/2023 Road Map RB |
| ERB-45 | Pelaporan RB Format Kurang Memadai / Timeline Tidak Sesuai | RB-PELAPORAN | MEDIUM | Permenpan-RB evaluasi RB |
| ERB-46 | Data Dukung Berupa Matriks, Bukan Laporan Hasil Formal | RB-BUKTI | MEDIUM | Permenpan-RB + SAIPI 2300 |
| ERB-47 | Pembangunan Zona Integritas Stagnan Lintas Tahun | RB-ZI | HIGH | Permenpan-RB 90/2021 ZI WBK/WBBM |

## Kategori yang dipakai

- `RB-OUTCOME` — pengukuran outcome/dampak rencana aksi (bukan sekadar output sesuai)
- `RB-PELAPORAN` — kualitas & ketepatan waktu pelaporan RB (LHEI)
- `RB-BUKTI` — kualitas data dukung (laporan hasil vs matriks)
- `RB-ZI` — pembangunan Zona Integritas (WBK/WBBM)
- `RB-RENAKSI` — kelengkapan & relevansi rencana aksi RB (General + Tematik)

## Sumber data pattern

Pattern di folder ini disusun dari LHE RB Inspektorat II TA 2024–2025:

- LHE on-going RB TW3 2025 (catatan EkDig/Itjen)
- LHE RB TW4 BAKTI 2024 (100% sesuai, tanpa pengukuran outcome)
- LHE RB TW4 Ekdig/Wasdig 2025; LHE RB TW4 PPI/Itjen 2024
- LKE RB Kemkomdigi 2024–2025 (ZI 16,67% flat 2 tahun; maturitas SPIP +0,75pp)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-33 maturitas stagnan, P-34 ZI flat)
- [[lhe-on-going-rb-tw3-2025]] / [[lke-rb-kemkomdigi-2024-2025]]
- [[evaluasi-sakip/README]] — keterkaitan RB & AKIP
- [[framework-evaluasi-rb]] / [[penilaian-internal-zi-2026]]

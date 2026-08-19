<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-spip/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Evaluasi SPIP

Index pattern temuan yang berlaku untuk skill `evaluasi-spip`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| ESP-35 | Skor Penilaian Mandiri > Penjaminan Kualitas (Optimism Bias) | SPIP-MATURITAS | HIGH | PP 60/2008 + Perka BPKP 5/2021 |
| ESP-36 | Register Risiko Strategis & RTP Belum Ada/Dikomunikasikan | SPIP-MR | HIGH | PP 60/2008 + Perka BPKP 5/2021 (area MRI) |
| ESP-37 | Aplikasi SPIP Bermasalah / Kertas Kerja Tidak Terisi | SPIP-SISTEM | MEDIUM | Perka BPKP 5/2021 |
| ESP-38 | Kompetensi SDM Penyelenggara SPIP Belum Merata | SPIP-SDM | MEDIUM | Perka BPKP 5/2021 (area kapabilitas) |

## Kategori yang dipakai

- `SPIP-MATURITAS` — skor maturitas penyelenggaraan SPIP (+ MRI + IEPK)
- `SPIP-MR` — manajemen risiko (register risiko strategis, RTP)
- `SPIP-SISTEM` — aplikasi/sistem informasi SPIP & kertas kerja
- `SPIP-SDM` — kompetensi penyelenggara
- `SPIP-LINGKUNGAN` — lingkungan pengendalian (kode etik, integritas)
- `SPIP-AOI` — Area of Improvement hasil penjaminan kualitas

## Sumber data pattern

Pattern di folder ini disusun dari Laporan Penjaminan Kualitas SPIP Inspektorat II TA 2025:

- Laporan Penjaminan Kualitas SPIP Kemkomdigi Final 2025 (maturitas 3,801 "Terdefinisi")
- Penjaminan Kualitas SPIP Ekdig (4,238 "Terkelola") / Wasdig (3,191) / Itjen (3,356)
- Laporan Sementara SPIP Kemkomdigi 2025 (9 catatan AoI; Renstra belum ditetapkan)
- Atensi Progres SPIP & MR 2025 (KK Lead II kosong; MR DJED/DJPRD 0%)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-33 maturitas stagnan, P-28 sistem belum early warning)
- [[laporan-penjaminan-kualitas-spip-kemkomdigi-final-2025]]
- [[evaluasi-manajemen-risiko/README]] — pattern evaluasi MR (terkait MRI)
- [[framework-evaluasi-spip]]

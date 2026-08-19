<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Audit Kinerja

Index pattern temuan yang berlaku untuk skill `audit-kinerja`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| AK-17 | Sistem/Teknologi Pengendalian Dapat Di-bypass (Efektivitas Rendah) | KINERJA-EFEKTIVITAS | CRITICAL | PP 8/2006 + SAIPI 2200; uji 3E |
| AK-18 | Hasil Deteksi/Crawling Tidak Ditindaklanjuti Sampai Tuntas | KINERJA-PROSES | HIGH | SAIPI 2300 + SOP penanganan konten |
| AK-19 | Tumpang Tindih Fungsi Antar-Sistem/Unit (Inefisiensi) | KINERJA-EFISIENSI | HIGH | PP 8/2006 prinsip efisiensi |
| AK-20 | Layanan Baru Diluncurkan dengan Kelemahan Tata Kelola Hulu + Keamanan Hilir | KINERJA-TATAKELOLA | HIGH | UU 27/2022 PDP + tata kelola SPBE |
| AK-21 | Capaian Kinerja Dilaporkan Tinggi tetapi Tidak Dapat Diverifikasi Sumbernya | KINERJA-DATA | MEDIUM | SAIPI 2300 bukti audit |
| AK-22 | Formula Tarif/Indikator Belum Mencerminkan Nilai Ekonomi/Outcome | KINERJA-DESAIN | MEDIUM | PP 8/2006 + pedoman penyusunan formula |

## Kategori yang dipakai

- `KINERJA-EFEKTIVITAS` — uji apakah tujuan/outcome tercapai (Efektif)
- `KINERJA-EFISIENSI` — uji rasio output terhadap input, tumpang tindih (Efisien)
- `KINERJA-EKONOMIS` — uji kehematan biaya perolehan input (Ekonomis)
- `KINERJA-PROSES` — proses bisnis end-to-end (deteksi → tindak lanjut → closure)
- `KINERJA-TATAKELOLA` — tata kelola layanan/sistem (hulu klasifikasi, hilir keamanan)
- `KINERJA-DATA` — keterverifikasian data capaian kinerja
- `KINERJA-DESAIN` — desain indikator/formula/tarif

## Sumber data pattern

Pattern di folder ini disusun dari LHP Kinerja BPK + audit kinerja Inspektorat II TA 2024–2026:

- LHP Kinerja BPK PSTE TA 2019 s.d. Sem I 2024 (14/LHP/XVI/02/2025) — TKPPSE efektivitas 22,44%
- LHP Kinerja Konten — Rencana Aksi BPK 2025 — CSE 3,84jt crawling belum verifikasi, tumpang tindih CNS/CSE/RTBH
- LHP Kinerja IPFR-ISR 2026 (17/T/LHP/DJPKN-III/PPN.02/01/2026) — formula BHP IPFR
- Audit Kinerja Layanan Klasifikasi Gim/IGRS (ST-92, 11 Mei–26 Jun 2026)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk 40 pattern lintas skill (P-29, P-30, P-35, P-40)
- [[reviu-pengadaan/README]] — pattern reviu Pengadaan
- [[pola-temuan-berulang]] — 9 pola berulang lintas LHP/LHR

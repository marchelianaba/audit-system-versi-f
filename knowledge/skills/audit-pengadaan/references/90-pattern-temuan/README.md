<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Audit Pengadaan

Index pattern temuan yang berlaku untuk skill `audit-pengadaan`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| AP-23 | Pekerjaan Berjalan & Ditagihkan Tanpa Kontrak Formal | PBJ-KONTRAK | CRITICAL | Perpres 16/2018 Pasal 1(18) + Perpres 46/2025 Pasal 9(1)f² |
| AP-24 | SLA Tidak Termonitor / Realisasi Jauh di Bawah Target Kontrak | PBJ-SLA | HIGH | Kontrak/SLA + Perpres 16/2018 Pasal 27 |
| AP-25 | Data Prestasi Kerja Tidak Memadai untuk Verifikasi Tagihan | PBJ-PEMBAYARAN | HIGH | PMK Pelaksanaan Anggaran + bukti dukung tagihan |
| AP-26 | Pembayaran Retroaktif Tidak Memenuhi 3 Syarat LKPP | PBJ-PEMBAYARAN | CRITICAL | Surat LKPP 22441/D.4.1/10/2025 |
| AP-27 | Vendor Lock-in pada Infrastruktur Kritis (Tanpa Exit Strategy) | PBJ-KONTRAK | HIGH | Perpres 16/2018 Pasal 6 + prinsip persaingan sehat |
| AP-28 | Kelebihan Pembayaran Akibat Insiden Tanpa Adjustment SLA | PBJ-PEMBAYARAN | HIGH | Kontrak klausul force majeure/SLA |
| AP-29 | Kesalahan Kurs/Klasifikasi Akun pada Pembayaran | PBJ-PEMBAYARAN | MEDIUM | Perjanjian + SAP + ketentuan kurs JISDOR |

## Kategori yang dipakai

- `PBJ-KONTRAK` — keberadaan & substansi kontrak (ada/tidak, exit strategy, vendor lock-in)
- `PBJ-SLA` — pemenuhan Service Level Agreement & monitoring
- `PBJ-PEMBAYARAN` — kewajaran pembayaran, bukti prestasi, retroaktif, kurs, klasifikasi akun
- `PBJ-ASET` — pencatatan aset hasil pengadaan (BAUP→BAPL, KDP, SITAC)

## Sumber data pattern

Pattern di folder ini disusun dari LHA audit pengadaan Inspektorat II + temuan BPK TA 2023–2026:

- LHA OM TKPPSE 2024/2025 (SLA 50,12%; Rp57,34M tagihan tanpa kontrak)
- DHA Tahap-2 + KHA Revisi-2 OM TKPPSE (syarat LKPP retroaktif; data Zabbix/Log Server)
- BPK SPI LK Kominfo 2024 (PDNS Rp2,20M, SATRIA kurs Rp1,51M, salah akun Rp84,95M, OM TKPPSE Rp4,66M)
- BPK LHP LK 2023 (BTS 4G OM Rp22,66M, IP Hub SATRIA Rp216,86M)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-01, P-02, P-03, P-04, P-07, P-32)
- [[reviu-pengadaan/README]] — pattern reviu Pengadaan (pre-award)
- [[pemantauan-pengadaan/README]] — pattern pemantauan Pengadaan (ongoing)

<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/AP-23-pekerjaan-tanpa-kontrak.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AP-23
skill: audit-pengadaan
kategori: PBJ-KONTRAK
severity: CRITICAL
judul: "Pekerjaan Berjalan & Ditagihkan Tanpa Kontrak Formal"
kriteria_baku: "Perpres 16/2018 Pasal 1 angka 18 + Perpres 46/2025 Pasal 9 ayat (1) huruf f angka 2"
tags: [kontrak, tanpa-kontrak, om-tkppse, retroaktif, sotk, audit-pengadaan]
---

# AP-23: Pekerjaan Berjalan & Ditagihkan Tanpa Kontrak Formal

## Pattern Kondisi

Pekerjaan/layanan (mis. OM, telekomunikasi, hosting) telah berjalan dan ditagihkan, tetapi **tidak didukung kontrak formal** pada saat pelaksanaan. Indikator umum:

- Layanan berjalan berbulan-bulan sebelum kontrak ditandatangani
- Kontrak ditandatangani **retroaktif** (durasi sangat singkat menutup periode yang sudah lewat)
- Hanya ada *Surat Perintah Kelanjutan Pekerjaan* / penunjukan tanpa kontrak
- Tagihan masuk tanpa nomor kontrak referensi
- Metode pengadaan langsung per lokasi/bulan menghasilkan ribuan tagihan

## Kriteria

Perpres 16/2018 Pasal 1 angka 18 — Kontrak adalah perjanjian tertulis antara PPK dengan Penyedia; pembayaran wajib didasari kontrak. Perpres 46/2025 Pasal 9(1)f² membuka jalur kontrak/pembayaran khusus dengan **syarat ketat** (lihat AP-26).

## Akibat

1. Pembayaran berisiko hukum (tidak ada dasar kontraktual)
2. Nilai tagihan tidak dapat diyakini (mis. Rp57,34M tidak diakui)
3. Sengketa/gugatan vendor (mis. wanprestasi)
4. Temuan BPK material

## Bukti Yang Harus Dicari

| Dokumen | Section / Field | Yang dicari |
|---------|-----------------|-------------|
| DIPA | tanggal terbit | gap DIPA vs tanggal mulai pekerjaan |
| Kontrak | tanggal TTD + durasi | retroaktif? durasi vs periode kerja |
| Surat penunjukan/kelanjutan | dasar hukum | ada kontrak atau hanya surat perintah |
| Tagihan/invoice | nomor kontrak | referensi kontrak ada/tidak |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AP-23",
  "assigned_to": "{nama anggota}",
  "judul": "Tagihan {pekerjaan} Rp{X} Tanpa Dasar Kontrak Formal",
  "kondisi": "Pekerjaan {pekerjaan} berjalan {periode} dan ditagihkan Rp{X}, namun kontrak baru ditandatangani {tgl} secara retroaktif (durasi {n} hari). DIPA terbit {tgl} akibat transisi SOTK. Tagihan tidak mereferensikan nomor kontrak.",
  "kriteria": "Perpres 16/2018 Pasal 1(18) — pembayaran wajib didasari kontrak tertulis; Perpres 46/2025 Pasal 9(1)f² mensyaratkan kondisi khusus.",
  "akibat": "Pembayaran berisiko hukum; nilai tagihan tidak dapat diyakini; potensi sengketa/gugatan; temuan BPK material.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "kontrak ditandatangani 30 Des 2024 ..."}]
}
```

## Contoh Kasus Historis

- **LHA Verifikasi Tagihan OM TKPPSE 2024 (Rp57,34M)** — pekerjaan Apr-Nov 2024 tanpa kontrak; kontrak Desember 2024 retroaktif (durasi 6 hari); >3.000 tagihan per lokasi/bulan; nilai **TIDAK DAPAT DIYAKINI**. **BPK SPI LK 2024** — OM TKPPSE kelebihan Rp4,66M + utang Rp57,28M diakui tanpa dokumentasi kontrak. Lihat [[lha-verifikasi-tagihan-om-tkppse-2024-rp57m]], [[bpk-spi-lk-kominfo-2024]], [[pattern-temuan]] P-01.

## Catatan

- Pasangan reviu (pre-award): [[reviu-pengadaan/RP-09-kontrak-tanpa-kontrak-sotk]] dan [[reviu-pengadaan/RP-16-vendor-pjt-belum-berkontrak]].
- Bila retroaktif, uji AP-26 (3 syarat LKPP). Rekomendasi: SOP transisi kontrak lintas Ditjen.

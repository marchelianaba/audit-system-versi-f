<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/AP-25-data-prestasi-tidak-memadai.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AP-25
skill: audit-pengadaan
kategori: PBJ-PEMBAYARAN
severity: HIGH
judul: "Data Prestasi Kerja Tidak Memadai untuk Verifikasi Tagihan"
kriteria_baku: "PMK Pelaksanaan Anggaran + bukti dukung tagihan + SAIPI 2300"
tags: [prestasi-kerja, verifikasi-tagihan, zabbix, log-server, backfill, audit-pengadaan]
---

# AP-25: Data Prestasi Kerja Tidak Memadai untuk Verifikasi Tagihan

## Pattern Kondisi

Pekerjaan berjalan tetapi sistem monitoring/bukti prestasi tidak aktif atau tidak lengkap, sehingga sebagian tagihan tidak dapat diverifikasi. Indikator umum:

- Sistem monitoring (mis. Zabbix, Log Server) baru di-deploy setelah pekerjaan berjalan
- Sebagian lokasi/transaksi tanpa data prestasi (mis. 20 dari 58 site)
- Data prestasi di-*backfill* manual untuk periode lampau
- BAPL/BAUP/Berita Acara tidak tersedia untuk periode tertentu
- Selisih data lokasi antara prime contractor dan sub-penyedia

## Kriteria

PMK Pelaksanaan Anggaran + ketentuan bukti dukung tagihan + SAIPI 2300 — pembayaran wajib didasari bukti prestasi kerja yang memadai; tagihan tanpa bukti tidak dapat diyakini.

## Akibat

1. Nilai tagihan tidak dapat diyakini (mis. Rp4,66M – Rp49,06M)
2. Risiko kelebihan/kekurangan bayar
3. Potensi pembayaran atas layanan yang tidak terbukti diberikan

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Inventaris sistem monitoring | tanggal deploy vs mulai pekerjaan |
| Data prestasi per lokasi | kelengkapan (berapa site ada data) |
| BAPL/BAUP/BA prestasi | ketersediaan per periode |
| Rekonsiliasi prime vs sub | selisih data lokasi |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AP-25",
  "assigned_to": "{nama anggota}",
  "judul": "Rp{X} Tagihan {pekerjaan} Tidak Dapat Dinilai — Data Prestasi Tidak Memadai",
  "kondisi": "Verifikasi tagihan {pekerjaan} periode {periode}: {M} dari {N} lokasi tanpa data prestasi ({sistem monitoring} baru aktif {tgl}). Senilai Rp{X} ({pct}%) tidak dapat dinilai karena bukti prestasi tidak tersedia.",
  "kriteria": "PMK Pelaksanaan Anggaran + bukti dukung tagihan + SAIPI 2300 — pembayaran wajib didasari bukti prestasi memadai.",
  "akibat": "Nilai tagihan tidak dapat diyakini; risiko kelebihan/kekurangan bayar; pembayaran atas layanan tak terbukti.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "20 dari 58 site tanpa data Zabbix ..."}]
}
```

## Contoh Kasus Historis

- **DHA Tahap-2 OM TKPPSE 2024** — 20 dari 58 site tanpa data Zabbix/Log Server (Mar–3 Nov 2024); Rp49,06M (85,6%) tidak dapat dinilai. **KHA Revisi-2** — Rp4,78M tidak dapat diyakini (ketidaksesuaian perhitungan + data dukung kurang). Lihat [[dha-tahap2-om-tkppse-2024]], [[kha-revisi2-om-tkppse-2024-rp16-rp57]], [[pattern-temuan]] P-04.

## Catatan

- Pelajaran: investasi monitoring harus **bersamaan** dengan start layanan, bukan setelah.
- Rekomendasi: kontrak mewajibkan delivery data monitoring sebagai prasyarat penagihan.

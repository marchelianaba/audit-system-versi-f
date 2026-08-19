<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/AP-24-sla-tidak-termonitor.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AP-24
skill: audit-pengadaan
kategori: PBJ-SLA
severity: HIGH
judul: "SLA Tidak Termonitor / Realisasi Jauh di Bawah Target Kontrak"
kriteria_baku: "Kontrak/SLA + Perpres 16/2018 Pasal 27 (pelaksanaan kontrak)"
tags: [sla, monitoring, metro-e, liquidated-damages, om-tkppse, audit-pengadaan]
---

# AP-24: SLA Tidak Termonitor / Realisasi Jauh di Bawah Target Kontrak

## Pattern Kondisi

SLA kontrak menargetkan tingkat layanan tinggi (mis. ≥99,5% uptime) tetapi realisasi jauh di bawahnya, dan/atau tidak ada mekanisme monitoring SLA yang berjalan. Indikator umum:

- Realisasi SLA jauh di bawah target (mis. 50,12% vs 99,5%)
- Lokasi/link tertentu mati berbulan-bulan tanpa ditindaklanjuti (mis. Metro-E mati 1 tahun)
- Laporan SLA tidak ditampilkan konsisten; tidak ada *escalation matrix*
- Sub-penyedia (PJT) tidak melapor ke prime; prime tidak melapor ke PA/KPA
- *Liquidated damages* atas pelanggaran SLA tidak dikenakan

## Kriteria

Kontrak/SLA + Perpres 16/2018 Pasal 27 (pelaksanaan kontrak) — penyedia wajib memenuhi tingkat layanan yang diperjanjikan; ketidakpatuhan SLA dikenai konsekuensi (denda/liquidated damages) dan pemotongan pembayaran.

## Akibat

1. Pembayaran tidak sebanding dengan layanan riil (kelebihan bayar)
2. Tujuan layanan tidak tercapai (mis. konektivitas pemblokiran terganggu)
3. *Liquidated damages* yang seharusnya diterima negara tidak ditagih
4. Temuan BPK atas kelebihan pembayaran

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Kontrak/SLA | target uptime + klausul denda |
| Dashboard/laporan SLA bulanan | realisasi vs target |
| Tiket/log gangguan | durasi *downtime* per lokasi |
| Perhitungan pembayaran | apakah ada potongan SLA breach |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AP-24",
  "assigned_to": "{nama anggota}",
  "judul": "Realisasi SLA {layanan} Hanya {X}% vs Target {Y}% — Tanpa Pemotongan/Denda",
  "kondisi": "SLA {layanan} mensyaratkan {Y}% uptime; realisasi {X}%. {N} lokasi mati {durasi} tanpa ditindaklanjuti. Tidak ada dashboard SLA konsisten dan tidak dikenakan liquidated damages atas pelanggaran.",
  "kriteria": "Kontrak/SLA + Perpres 16/2018 Pasal 27 — penyedia wajib penuhi SLA; pelanggaran dikenai denda + pemotongan pembayaran.",
  "akibat": "Kelebihan pembayaran; tujuan layanan tidak tercapai; denda negara tidak ditagih; temuan BPK.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "SLA 50,12% vs target 99,5% ..."}]
}
```

## Contoh Kasus Historis

- **LHA OM TKPPSE 2024** — SLA pemenuhan **50,12% vs target 99,5%**; Metro-E 3 lokasi tidak berfungsi 1 tahun tanpa ditindaklanjuti; PT SUFI tidak melakukan SLA monitoring. **DHA Tahap-2** — KOS Smartfren SLA 52,82%. Lihat [[lha-om-tkppse-2024]], [[dha-tahap2-om-tkppse-2024]], [[pattern-temuan]] P-02.

## Catatan

- Rekomendasi: dashboard SLA *real-time*; klausul *liquidated damages* otomatis terhitung.
- Sinergi: AP-25 (data prestasi), [[reviu-pengadaan/RP-13-vendor-confidentiality-audit-trail]].

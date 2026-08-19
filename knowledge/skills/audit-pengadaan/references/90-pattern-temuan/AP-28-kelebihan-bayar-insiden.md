<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/AP-28-kelebihan-bayar-insiden.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AP-28
skill: audit-pengadaan
kategori: PBJ-PEMBAYARAN
severity: HIGH
judul: "Kelebihan Pembayaran Akibat Insiden Tanpa Adjustment SLA"
kriteria_baku: "Kontrak (klausul force majeure/SLA) + PMK Pelaksanaan Anggaran"
tags: [insiden, ransomware, pdns, downtime, adjustment-sla, kelebihan-bayar, audit-pengadaan]
---

# AP-28: Kelebihan Pembayaran Akibat Insiden Tanpa Adjustment SLA

## Pattern Kondisi

Terjadi insiden besar (mis. *downtime*, ransomware, bencana) yang menurunkan layanan, tetapi pembayaran tetap penuh tanpa penyesuaian (*adjustment*) sesuai layanan riil. Indikator umum:

- Insiden besar (downtime >24 jam) tetapi pembayaran continue penuh
- Tidak ada klausul/penerapan *SLA adjustment* atau *force majeure* yang men-trigger pemotongan
- Recovery data/layanan tidak terdokumentasi
- Tagihan periode terdampak tidak dikurangi

## Kriteria

Kontrak (klausul force majeure/SLA) + PMK Pelaksanaan Anggaran — pembayaran harus sebanding dengan layanan riil yang diterima; periode terdampak insiden wajib disesuaikan.

## Akibat

1. Kelebihan pembayaran atas layanan yang tidak diterima
2. Negara menanggung biaya insiden yang seharusnya jadi risiko penyedia
3. Temuan BPK atas kelebihan bayar

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Laporan insiden + recovery log | durasi & dampak downtime |
| Kontrak | klausul force majeure / SLA adjustment |
| Perhitungan pembayaran periode insiden | apakah ada pengurangan |
| BA layanan periode terdampak | tingkat layanan riil |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AP-28",
  "assigned_to": "{nama anggota}",
  "judul": "Kelebihan Pembayaran Rp{X} {layanan} Akibat Insiden Tanpa Adjustment",
  "kondisi": "Insiden {jenis} pada {tgl} menyebabkan downtime {durasi}; layanan {layanan} tetap dibayar penuh Rp{X} untuk periode {periode} tanpa adjustment SLA. Recovery tidak terdokumentasi; kontrak tidak men-trigger pemotongan.",
  "kriteria": "Kontrak (force majeure/SLA) + PMK Pelaksanaan Anggaran — pembayaran harus sebanding layanan riil; periode terdampak insiden wajib disesuaikan.",
  "akibat": "Kelebihan pembayaran atas layanan tak diterima; negara menanggung risiko penyedia; temuan BPK.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **BPK Temuan PDNS 2024** — insiden ransomware **Brain Cipher** 20 Juni 2024; PDNS-2 Surabaya *down* berbulan; kelebihan pembayaran **Rp2,20M** Juli-Agustus tanpa penyesuaian layanan riil. Lihat [[bpk-temuan-pdns-satria-2024]], [[bpk-spi-lk-kominfo-2024]], [[pattern-temuan]] P-32.

## Catatan

- Rekomendasi: klausul *SLA adjustment* untuk insiden siber wajib eksplisit; *incident postmortem* wajib untuk insiden besar.

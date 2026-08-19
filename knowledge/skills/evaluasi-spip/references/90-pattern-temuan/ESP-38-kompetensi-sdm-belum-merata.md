<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-spip/ESP-38-kompetensi-sdm-belum-merata.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESP-38
skill: evaluasi-spip
kategori: SPIP-SDM
severity: MEDIUM
judul: "Kompetensi SDM Penyelenggara SPIP Belum Merata"
kriteria_baku: "Perka BPKP 5/2021 (area kapabilitas penyelenggaraan SPIP)"
tags: [spip, sdm, kompetensi, mr, kapabilitas, perka-bpkp-5]
---

# ESP-38: Kompetensi SDM Penyelenggara SPIP Belum Merata

## Pattern Kondisi

Kompetensi pegawai penyelenggara SPIP/MR belum merata, sehingga kualitas penyelenggaraan tidak seragam. Indikator umum:

- Standar kompetensi penyelenggara SPIP/MR belum ditetapkan
- Sebagian pegawai belum mengikuti pelatihan SPIP/MR
- Pemahaman atas Three Lines Model / pengendalian belum merata
- Penyelenggaraan bergantung pada beberapa individu kunci

## Kriteria

Perka BPKP 5/2021 (area kapabilitas) — penyelenggaraan SPIP memerlukan SDM yang kompeten, dengan standar kompetensi yang ditetapkan dan pelatihan yang memadai.

## Akibat

1. Kualitas penyelenggaraan SPIP tidak seragam antar-unit
2. Risiko tidak teridentifikasi/tertangani memadai
3. Skor maturitas tertahan (komponen kapabilitas)

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Standar kompetensi SPIP/MR | ada/tidak ditetapkan |
| Daftar pelatihan SPIP/MR | cakupan pegawai yang sudah dilatih |
| Catatan AoI | kompetensi MR pegawai |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESP-38",
  "assigned_to": "{nama anggota}",
  "judul": "Kompetensi SDM Penyelenggara SPIP {satker} Belum Merata",
  "kondisi": "Penjaminan kualitas SPIP {satker}: standar kompetensi penyelenggara SPIP/MR belum ditetapkan; {sebagian} pegawai belum ikut pelatihan; pemahaman Three Lines Model belum merata; penyelenggaraan bergantung pada individu kunci.",
  "kriteria": "Perka BPKP 5/2021 (area kapabilitas) — penyelenggaraan SPIP perlu SDM kompeten dengan standar kompetensi + pelatihan memadai.",
  "akibat": "Kualitas penyelenggaraan tidak seragam; risiko tidak tertangani memadai; skor maturitas tertahan.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "kompetensi MR belum merata ..."}]
}
```

## Contoh Kasus Historis

- **Laporan Penjaminan Kualitas SPIP Kemkomdigi Final 2025** — AoI: kompetensi MR pegawai belum merata + komunikasi strategi MR. **LHE Manajemen Risiko 2026** — standar kompetensi SDM MR belum ditetapkan; Three Lines Model belum diimplementasikan optimal. Lihat [[laporan-penjaminan-kualitas-spip-kemkomdigi-final-2025]], [[lhe-manajemen-risiko-2026]].

## Catatan

- Rekomendasi: tetapkan standar kompetensi SPIP/MR + training merata; selaras dengan strategi SDM Renstra ([[renstra-itjen-2025-2029]] 3.2.2).
- Sinergi: [[evaluasi-manajemen-risiko/EMR-42-pedoman-mr-usang]].

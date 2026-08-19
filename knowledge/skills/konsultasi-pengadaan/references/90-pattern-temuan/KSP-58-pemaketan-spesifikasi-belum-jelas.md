<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/konsultasi-pengadaan/KSP-58-pemaketan-spesifikasi-belum-jelas.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: KSP-58
skill: konsultasi-pengadaan
kategori: PBJ-HPS
severity: MEDIUM
judul: "Pemaketan/Spesifikasi Belum Jelas Saat Penyusunan HPS"
kriteria_baku: "Perpres 16/2018 Pasal 18 (perencanaan) + Pasal 26 (HPS)"
tags: [pemaketan, spesifikasi, hps, advisory, konsultasi-pengadaan]
---

# KSP-58: Pemaketan/Spesifikasi Belum Jelas Saat Penyusunan HPS

## Pattern Kondisi

Pada konsultasi penyusunan HPS, pemaketan dan/atau spesifikasi teknis belum jelas/terdefinisi. Indikator umum:

- Pemaketan (paket vs sub-paket) belum diputuskan saat HPS disusun
- Spesifikasi teknis masih umum/ambigu
- HPS disusun tanpa basis spesifikasi final
- Review final HPS dilakukan tanpa kelengkapan pemaketan

## Kriteria

Perpres 16/2018 Pasal 18 (perencanaan: pemaketan) + Pasal 26 (HPS berbasis spesifikasi) — HPS harus didasarkan pada pemaketan & spesifikasi teknis yang jelas.

## Akibat

1. HPS tidak akurat (basis spesifikasi lemah)
2. Risiko revisi HPS/pemaketan di tengah proses
3. Pemilihan berisiko gagal/sengketa

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Dokumen pemaketan | keputusan paket/sub-paket |
| Spesifikasi teknis | kelengkapan & ketegasan |
| Draft HPS | basis spesifikasi yang dipakai |

## Format Temuan / Catatan Advisory (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-KSP-58",
  "assigned_to": "{nama anggota}",
  "judul": "Pemaketan/Spesifikasi {paket} Belum Jelas Saat Penyusunan HPS",
  "kondisi": "Konsultasi penyusunan HPS {paket}: pemaketan belum diputuskan + spesifikasi teknis masih umum/ambigu; review final HPS dilakukan tanpa kelengkapan pemaketan & spesifikasi final.",
  "kriteria": "Perpres 16/2018 Pasal 18 (pemaketan) + Pasal 26 (HPS) — HPS harus berbasis pemaketan & spesifikasi teknis yang jelas.",
  "akibat": "HPS tidak akurat; risiko revisi HPS/pemaketan di tengah proses; pemilihan berisiko gagal/sengketa.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **ST-90 Konsultasi Teknis HPS, Review Final, Pemaketan, Mini-Kompetisi E-Katalog DJED (12-14 Mei 2026)** — agenda mencakup penyusunan pemaketan + review final HPS; IR II hadir sebagai advisor pra-pengadaan untuk memastikan pemaketan & HPS memadai. Lihat [[surat-tugas-ir2-mei-2026]] (ST-90).

## Catatan

- Sinergi: [[reviu-pengadaan/RP-08-hps-rfi-minimum]] (kewajaran HPS), [[reviu-rka-kl/RKA-04-tor-tanpa-metode-pengadaan]].
- Rekomendasi advisory: finalisasi pemaketan & spesifikasi sebelum HPS dikunci.

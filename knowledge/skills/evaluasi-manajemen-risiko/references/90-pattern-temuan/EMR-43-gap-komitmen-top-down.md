<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-manajemen-risiko/EMR-43-gap-komitmen-top-down.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: EMR-43
skill: evaluasi-manajemen-risiko
kategori: MR-TATAKELOLA
severity: CRITICAL
judul: "Gap Komitmen Top-Down (Pemilik Risiko Tertinggi Belum Lengkap)"
kriteria_baku: "Pedoman MR + Three Lines Model (IIA 2020) — Governing Body"
tags: [mr, top-down, menteri, governing-body, three-lines-model, evaluasi-mr]
---

# EMR-43: Gap Komitmen Top-Down (Pemilik Risiko Tertinggi Belum Lengkap)

## Pattern Kondisi

Dokumen MR pada level pemilik risiko tertinggi (Menteri) justru paling tidak lengkap, menandakan gap komitmen yang bersifat *top-down*. Indikator umum:

- Skor MR level Menteri/Kementerian terendah dibanding satker (mis. 40% vs 60–93%)
- Komponen kunci (Penanganan, Pemantauan, Piagam Risiko) kosong di level tertinggi
- Satker bawah mencontoh ketidaklengkapan level atas (mis. DJED 60%)
- Korelasi: makin tinggi level, makin rendah kelengkapan

## Kriteria

Pedoman MR + Three Lines Model (IIA 2020) — *Governing Body* (Menteri) menetapkan arah & komitmen MR; tanpa komitmen pemilik risiko tertinggi, pelembagaan MR di bawahnya lemah.

## Akibat

1. Sinyal komitmen lemah menyebar ke seluruh organisasi
2. Skor maturitas MR Kemkomdigi turun secara agregat
3. Risiko strategis kementerian tidak dikelola di level tertinggi

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| LHE MR per level | skor Menteri vs Eselon I vs satker |
| Komponen MR level Menteri | kelengkapan 5 komponen |
| Pola antar-level | korelasi level vs kelengkapan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-EMR-43",
  "assigned_to": "{nama anggota}",
  "judul": "Gap Komitmen MR Top-Down — Level {tertinggi} Hanya {X}% (Terendah)",
  "kondisi": "Komparasi LHE MR TW {n}: level {Menteri} {X}% (terendah) vs Eselon I {a}%, satker {b}%. Komponen Penanganan/Pemantauan/Piagam kosong di level tertinggi. Pola: makin tinggi level, makin rendah kelengkapan — gap bersifat top-down.",
  "kriteria": "Pedoman MR + Three Lines Model — Governing Body menetapkan arah & komitmen MR; tanpa komitmen pemilik risiko tertinggi, pelembagaan MR lemah.",
  "akibat": "Sinyal komitmen lemah menyebar ke organisasi; skor maturitas MR agregat turun; risiko strategis tidak dikelola di level tertinggi.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Menteri 40% < DJED 60% < Itjen/DJPRD 93,3% ..."}]
}
```

## Contoh Kasus Historis

- **Quartet LHE MR TW I 2026** — **Menteri 40%** (3 komponen kosong) < **DJED 60%** (7/7 satker gap) < **Itjen/DJPRD 93,3%**. Pola top-down: bila Menteri belum komit (ND-127), satker DJED juga belum komit (ND-126). Lihat [[nota-dinas-ir2-april-2026]] (ND-124–127), [[pattern-temuan]] P-33.

## Catatan

- Severity CRITICAL karena akar masalah ada di puncak organisasi.
- Rekomendasi: eskalasi ke Menteri untuk lengkapi dokumen MR level tertinggi sebagai *tone at the top*.
- Sinergi: EMR-39, EMR-40, EMR-41 (semua gejala dari gap ini).

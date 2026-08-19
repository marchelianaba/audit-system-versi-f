<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-sakip/ESK-31-pengukuran-kinerja-terendah.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESK-31
skill: evaluasi-sakip
kategori: SAKIP-PENGUKURAN
severity: HIGH
judul: "Komponen Pengukuran Kinerja Bernilai Terendah pada Evaluasi AKIP"
kriteria_baku: "Permenpan-RB 88/2021 (komponen Pengukuran Kinerja bobot 30%)"
tags: [sakip, akip, pengukuran-kinerja, decision-tool, permenpanrb-88]
---

# ESK-31: Komponen Pengukuran Kinerja Bernilai Terendah

## Pattern Kondisi

Pada evaluasi AKIP, komponen **Pengukuran Kinerja** memperoleh % capaian terendah dibanding Perencanaan/Pelaporan/Evaluasi. Indikator umum:

- Capaian Pengukuran < komponen lain (mis. 57,4% vs 71–77%)
- Pengukuran masih administratif, belum menyentuh substansi permasalahan
- Penilaian bulanan tidak selaras dengan kumulatif tahunan
- Hasil pengukuran belum dipakai untuk keputusan (reward/punishment, strategi, kompetensi)

## Kriteria

**Permenpan-RB 88/2021** — Pengukuran Kinerja berbobot **30%**; harus berbasis data andal, selaras antar-periode, dan dimanfaatkan sebagai dasar pengambilan keputusan.

## Akibat

1. Nilai AKIP tertahan/stagnan (lihat ESK-30)
2. Keputusan manajemen tidak berbasis data kinerja
3. Capaian RO/IKU sulit diverifikasi (lihat ESK-34 + [[reviu-rka-kl/RKA-02-ro-tanpa-parameter-keberhasilan]])

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| LHE AKIP (rincian komponen) | skor & % capaian per komponen |
| Aplikasi kinerja (e-SAKIP/SKP) | dipakai sebagai decision tool? |
| Laporan bulanan vs tahunan | konsistensi penilaian |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESK-31",
  "assigned_to": "{nama anggota}",
  "judul": "Komponen Pengukuran Kinerja {satker} Bernilai Terendah ({X}%)",
  "kondisi": "Evaluasi AKIP {YYYY} {satker}: Pengukuran Kinerja {X}% (nilai {n} dari bobot 30), terendah vs Perencanaan {a}%, Pelaporan {b}%, Evaluasi {c}%. Pengukuran masih administratif; penilaian bulanan-kumulatif tidak selaras; hasil belum jadi decision tool.",
  "kriteria": "Permenpan-RB 88/2021 — Pengukuran Kinerja berbobot 30%; harus andal, selaras antar-periode, dan dimanfaatkan untuk keputusan.",
  "akibat": "Nilai AKIP stagnan; keputusan tidak berbasis data; capaian RO/IKU sulit diverifikasi.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Pengukuran Kinerja 17,21 (57,4%) ..."}]
}
```

## Contoh Kasus Historis

- **ND-133 Atensi SAKIP** — Pengukuran Kinerja Kemkomdigi 2025 = **57,4%** (nilai 17,21 dari bobot 30), **terendah** vs Perencanaan 71,6%, Pelaporan 75,3%, Evaluasi 76,6%. Total AKIP 69,14. Lihat [[nota-dinas-ir2-mei-2026]] (ND-133), [[pattern-temuan]] P-33.

## Catatan

- Rekomendasi: jadikan aplikasi janji kinerja & SKP sebagai *decision tool*; selaraskan penilaian bulanan-kumulatif.
- Sinergi: ESK-30, ESK-32, ESK-34.

<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-spip/ESP-35-skor-pm-lebih-tinggi-qa.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESP-35
skill: evaluasi-spip
kategori: SPIP-MATURITAS
severity: HIGH
judul: "Skor Penilaian Mandiri Lebih Tinggi dari Penjaminan Kualitas (Optimism Bias)"
kriteria_baku: "PP 60/2008 tentang SPIP + Perka BPKP 5/2021 Penilaian Maturitas SPIP Terintegrasi"
tags: [spip, maturitas, penilaian-mandiri, penjaminan-kualitas, optimism-bias, perka-bpkp-5]
---

# ESP-35: Skor Penilaian Mandiri Lebih Tinggi dari Penjaminan Kualitas

## Pattern Kondisi

Skor maturitas SPIP hasil **penilaian mandiri** satker lebih tinggi dari hasil **penjaminan kualitas** APIP, menunjukkan *optimism bias*. Indikator umum:

- Selisih skor PM vs QA signifikan (mis. 4,115 → 3,801)
- Komponen MRI/IEPK turun saat penjaminan
- Bukti dukung tidak memadai untuk skor yang diklaim
- Skor turun ke level lebih rendah (mis. "Terkelola" → "Terdefinisi")

## Kriteria

PP 60/2008 + Perka BPKP 5/2021 — maturitas SPIP dinilai atas 3 komponen (SPIP, MRI, IEPK) berbasis bukti; penilaian mandiri harus dapat dipertanggungjawabkan dan dikonfirmasi penjaminan kualitas.

| Interval | Tingkat Maturitas |
|---|---|
| ≥4,50 | Optimum |
| 4,00–4,50 | Terkelola dan Terukur |
| 3,00–4,00 | **Terdefinisi** |
| 2,00–3,00 | Berkembang |
| 1,00–2,00 | Rintisan |

## Akibat

1. Gambaran pengendalian internal terlalu optimistis (risiko tidak terkelola)
2. Skor turun saat penjaminan → kredibilitas penilaian mandiri lemah
3. Area perbaikan tidak teridentifikasi tepat

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Laporan penilaian mandiri | skor klaim per komponen |
| Laporan penjaminan kualitas | skor hasil QA + selisih |
| Kertas kerja + bukti dukung | kecukupan bukti per parameter |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESP-35",
  "assigned_to": "{nama anggota}",
  "judul": "Skor SPIP Penilaian Mandiri {satker} ({a}) Lebih Tinggi dari Penjaminan Kualitas ({b})",
  "kondisi": "Penilaian mandiri SPIP {satker} skor {a} ('{level_a}'), namun penjaminan kualitas APIP {b} ('{level_b}'). Selisih akibat bukti dukung tidak memadai pada komponen {SPIP/MRI/IEPK}.",
  "kriteria": "PP 60/2008 + Perka BPKP 5/2021 — maturitas SPIP dinilai berbasis bukti; penilaian mandiri harus dapat dipertanggungjawabkan.",
  "akibat": "Gambaran pengendalian terlalu optimistis; kredibilitas penilaian mandiri lemah; area perbaikan tidak teridentifikasi tepat.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "PM 4,115 → QA 3,801 ..."}]
}
```

## Contoh Kasus Historis

- **Laporan Penjaminan Kualitas SPIP Kemkomdigi Final 2025** — Maturitas SPIP turun dari PM **4,115 → 3,801 "Terdefinisi"**; MRI 4,165 → 3,667; IEPK 3,253 → 3,080. Lihat [[laporan-penjaminan-kualitas-spip-kemkomdigi-final-2025]], [[pattern-temuan]] P-33.

## Catatan

- Pertanyaan kunci agen: "Tunjukkan bukti dukung untuk skor yang diklaim di penilaian mandiri."
- Sinergi: ESP-36 (register risiko strategis = penyebab utama turunnya MRI).

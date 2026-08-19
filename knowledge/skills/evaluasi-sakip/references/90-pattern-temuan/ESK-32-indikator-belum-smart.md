<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-sakip/ESK-32-indikator-belum-smart.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESK-32
skill: evaluasi-sakip
kategori: SAKIP-PERENCANAAN
severity: HIGH
judul: "Indikator Kinerja Belum SMART / Berorientasi Proses (Bukan Hasil)"
kriteria_baku: "Permenpan-RB 88/2021 + Perpres 29/2014 SAKIP"
tags: [sakip, indikator-smart, orientasi-hasil, sasaran-strategis, permenpanrb-88]
---

# ESK-32: Indikator Kinerja Belum SMART / Berorientasi Proses

## Pattern Kondisi

Sasaran/indikator kinerja masih berorientasi output/kegiatan/proses dan belum memenuhi prinsip SMART. Indikator umum:

- Indikator mengukur **aktivitas/proses** (mis. "% sosialisasi") bukan **hasil/outcome**
- Indikator tidak relevan dengan sasaran strategis yang diembannya
- Target memakai satuan yang tidak tepat (mis. persentase, bukan besaran rupiah PNBP)
- Indikator tidak *Specific/Measurable/Achievable/Relevant/Time-bound*

## Kriteria

Permenpan-RB 88/2021 (komponen Perencanaan Kinerja, bobot 30%) + Perpres 29/2014 — sasaran harus berorientasi hasil, indikator harus SMART dan selaras dengan sasaran strategis.

## Akibat

1. Capaian "tinggi" tidak mencerminkan hasil nyata
2. Nilai komponen Perencanaan tertahan
3. Evaluasi capaian menjadi *misleading*

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| PK / Renstra (matriks sasaran-indikator) | keselarasan indikator dengan sasaran |
| Catatan LHE Perencanaan | indikator berorientasi proses/output |
| Definisi & satuan target | tepat-tidaknya satuan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESK-32",
  "assigned_to": "{nama anggota}",
  "judul": "Indikator '{indikator}' {satker} Belum SMART / Berorientasi Proses",
  "kondisi": "Indikator '{indikator}' pada sasaran '{sasaran}' {satker}: (a) mengukur proses/aktivitas bukan hasil; (b) tidak relevan dengan sasaran strategis; (c) satuan target {tidak tepat}. Belum memenuhi prinsip SMART.",
  "kriteria": "Permenpan-RB 88/2021 + Perpres 29/2014 — sasaran berorientasi hasil; indikator SMART & selaras sasaran strategis.",
  "akibat": "Capaian tinggi tidak mencerminkan hasil nyata; nilai komponen Perencanaan tertahan; evaluasi misleading.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Persentase Sosialisasi pelayanan publik ..."}]
}
```

## Contoh Kasus Historis

- **ND-133 Atensi SAKIP** — contoh: Balai Monitoring SFR "Persentase Sosialisasi pelayanan publik" tidak relevan dengan sasaran "Meningkatnya Kepatuhan & Kualitas Pengendalian SFR"; DJPRD "Persentase Realisasi PNBP" belum gambarkan kualitas layanan + target pakai persentase bukan rupiah. Lihat [[nota-dinas-ir2-mei-2026]] (ND-133), [[lhe-akip-eksternal-kemenpanrb-2023-2024]].

## Catatan

- Sinergi kuat dengan [[reviu-rka-kl/RKA-02-ro-tanpa-parameter-keberhasilan]] (indikator SMART di RKA-K/L) dan [[audit-kinerja/AK-21-capaian-tidak-traceable]].
- Rekomendasi: reformulasi sasaran & indikator berorientasi hasil.

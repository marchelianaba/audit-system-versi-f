<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-manajemen-risiko/EMR-40-piagam-risiko-belum-ttd.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: EMR-40
skill: evaluasi-manajemen-risiko
kategori: MR-KOMITMEN
severity: HIGH
judul: "Piagam Risiko Belum Ditandatangani/Diunggah"
kriteria_baku: "Pedoman MR + Three Lines Model (IIA 2020) — komitmen pemilik risiko"
tags: [mr, piagam-risiko, komitmen-pimpinan, formalisasi, evaluasi-mr]
---

# EMR-40: Piagam Risiko Belum Ditandatangani/Diunggah

## Pattern Kondisi

Piagam Risiko sebagai formalisasi komitmen pimpinan belum ditandatangani/diunggah ke sistem. Indikator umum:

- Piagam Risiko belum ditandatangani pimpinan satker (mis. 7/7 satker)
- Belum diunggah ke SIMR meskipun komponen lain terisi
- Komitmen budaya risiko belum terlembaga
- Pola berkorelasi dengan pemantauan kosong (EMR-39)

## Kriteria

Pedoman MR + Three Lines Model (IIA 2020) — pemilik risiko (lini pertama/pimpinan) wajib menyatakan komitmen formal melalui Piagam Risiko sebagai dasar pelembagaan budaya risiko.

## Akibat

1. Komitmen pimpinan atas MR belum formal
2. Pelembagaan budaya risiko lemah
3. Berpotensi menurunkan skor maturitas MR Kemkomdigi

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Piagam Risiko per satker | status TTD + unggah |
| SIMR | dokumen Piagam terunggah? |
| Rekap per satker | berapa satker belum |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-EMR-40",
  "assigned_to": "{nama anggota}",
  "judul": "Piagam Risiko {satker} Belum Ditandatangani/Diunggah ({M}/{N} satker)",
  "kondisi": "Evaluasi MR {periode} {satker}: Piagam Risiko belum ditandatangani pimpinan + belum diunggah ke SIMR oleh {M} dari {N} satker. Formalisasi komitmen pimpinan belum terpenuhi.",
  "kriteria": "Pedoman MR + Three Lines Model — pemilik risiko wajib menyatakan komitmen formal melalui Piagam Risiko.",
  "akibat": "Komitmen pimpinan belum formal; pelembagaan budaya risiko lemah; berpotensi menurunkan skor maturitas MR.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Piagam Risiko: 0/7 satker ditandatangani ..."}]
}
```

## Contoh Kasus Historis

- **ND-126 LHE MR DJED TW I 2026** — **7/7 satker** belum tandatangan + unggah Piagam Risiko; **ND-127 Menteri** — Piagam Risiko belum ditandatangani Menteri (skor 40% "Perlu Perhatian"). Lihat [[nota-dinas-ir2-april-2026]] (ND-126/127), [[piagam-mr-itjen-2026]].

## Catatan

- Rekomendasi: mintakan TTD pimpinan + unggah ke SIMR.
- Sinergi: EMR-43 (Menteri sebagai pemilik risiko tertinggi belum komit = akar top-down).

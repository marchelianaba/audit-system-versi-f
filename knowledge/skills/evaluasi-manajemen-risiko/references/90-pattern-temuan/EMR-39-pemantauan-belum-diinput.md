<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-manajemen-risiko/EMR-39-pemantauan-belum-diinput.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: EMR-39
skill: evaluasi-manajemen-risiko
kategori: MR-PEMANTAUAN
severity: HIGH
judul: "Pemantauan Risiko Triwulanan Belum Diinput"
kriteria_baku: "Pedoman MR K/L + komponen pemantauan (siklus triwulanan)"
tags: [mr, pemantauan, triwulan, simr, evaluasi-mr]
---

# EMR-39: Pemantauan Risiko Triwulanan Belum Diinput

## Pattern Kondisi

Komponen Pemantauan Triwulanan dalam dokumen MR belum diinput/dilengkapi meskipun triwulan telah berakhir. Indikator umum:

- Pemantauan TW belum diinput oleh sebagian/seluruh satker (mis. 0/7 satker)
- Komponen lain (Konteks, Profil, Penanganan) lengkap tetapi Pemantauan kosong
- Tidak ada informasi perkembangan risiko/status mitigasi
- Pemantauan terlambat melewati batas akhir triwulan berikutnya

## Kriteria

Pedoman MR K/L — siklus MR mencakup pemantauan berkala (triwulanan) atas perkembangan risiko & efektivitas penanganan; hasil pemantauan menjadi dasar keputusan pimpinan.

## Akibat

1. Pimpinan tidak punya data akurat perkembangan risiko untuk keputusan
2. Skor maturitas MR menurun (komponen pemantauan kosong)
3. Mitigasi risiko tidak terpantau efektivitasnya

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| SIMR / form pemantauan | status pengisian Pemantauan TW per satker |
| Form I-III MR | kelengkapan 5 komponen |
| Rekap per satker | berapa satker sudah/belum input |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-EMR-39",
  "assigned_to": "{nama anggota}",
  "judul": "Pemantauan Risiko TW {n} {satker} Belum Diinput ({M}/{N} satker)",
  "kondisi": "Evaluasi MR TW {n} {YYYY} {satker}: komponen Konteks/Profil/Penanganan lengkap, namun Pemantauan TW {n} belum diinput oleh {M} dari {N} satker meskipun TW telah berakhir {tgl}. Tidak ada informasi perkembangan risiko/status mitigasi.",
  "kriteria": "Pedoman MR K/L — pemantauan berkala (triwulanan) wajib atas perkembangan risiko & efektivitas penanganan.",
  "akibat": "Pimpinan tidak punya data akurat untuk keputusan; skor maturitas MR menurun; mitigasi tidak terpantau.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Pemantauan TW I: 0/7 satker ..."}]
}
```

## Contoh Kasus Historis

- **ND-126 LHE MR DJED TW I 2026** — **7/7 satker** belum input Pemantauan TW I (+ Piagam Risiko); skor 60% "Cukup". **ND-124/125** (Itjen/DJPRD) — 2 satker belum input Pemantauan (skor 93,3%). Lihat [[nota-dinas-ir2-april-2026]] (ND-124–127), [[lhe-mr-triwulan-1-2026]], [[pattern-temuan]] P-33.

## Catatan

- Rekomendasi: lengkapi Pemantauan TW sebelum batas akhir TW berikutnya; SekDJ koordinasi kelengkapan.
- Sinergi: EMR-40 (Piagam Risiko), EMR-43 (gap top-down).

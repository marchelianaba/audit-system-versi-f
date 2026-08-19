<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-reformasi-birokrasi/ERB-46-data-dukung-matriks.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ERB-46
skill: evaluasi-reformasi-birokrasi
kategori: RB-BUKTI
severity: MEDIUM
judul: "Data Dukung Berupa Matriks, Bukan Laporan Hasil Formal"
kriteria_baku: "Permenpan-RB (evaluasi RB) + SAIPI 2300 (bukti memadai)"
tags: [rb, data-dukung, matriks, laporan-hasil, spip-eselon-i, evaluasi-rb]
---

# ERB-46: Data Dukung Berupa Matriks, Bukan Laporan Hasil Formal

## Pattern Kondisi

Bukti pendukung capaian RB hanya berupa matriks/checklist, bukan laporan hasil formal yang memadai. Indikator umum:

- Kertas kerja penilaian mandiri SPIP Eselon I belum lengkap (mis. 3/8)
- Data dukung berupa matriks, bukan Laporan Hasil formal
- TIM penilai belum men-deliver Laporan Hasil resmi
- Koordinasi SPIP & RB belum seamless

## Kriteria

Permenpan-RB (evaluasi RB) + SAIPI Standar 2300 — capaian RB harus didukung bukti yang memadai (laporan hasil formal), bukan sekadar matriks/checklist.

## Akibat

1. Capaian RB tidak dapat diyakini memadai
2. Penilaian RB General berisiko incomplete
3. Audit trail lemah

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Kertas kerja penilaian mandiri | kelengkapan (berapa dari total) |
| Data dukung capaian | matriks vs laporan hasil formal |
| BA/Laporan Hasil TIM | ada/tidak deliver formal |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ERB-46",
  "assigned_to": "{nama anggota}",
  "judul": "Data Dukung RB {satker} Berupa Matriks, Bukan Laporan Hasil Formal",
  "kondisi": "LHE RB General {satker} {periode}: kertas kerja penilaian mandiri SPIP Eselon I incomplete ({M}/{N}); data dukung berupa matriks, bukan Laporan Hasil formal; TIM belum deliver Laporan Hasil resmi.",
  "kriteria": "Permenpan-RB + SAIPI 2300 — capaian RB harus didukung bukti memadai (laporan hasil formal).",
  "akibat": "Capaian RB tidak dapat diyakini; penilaian RB General incomplete; audit trail lemah.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "kertas kerja SPIP eselon I 3/8; data dukung matriks ..."}]
}
```

## Contoh Kasus Historis

- **LHE on-going RB TW3 2025 (Itjen)** — 2 catatan RB General: kertas kerja penilaian mandiri SPIP Eselon I incomplete (**3/8**) + data dukung berupa matriks, bukan laporan hasil. Lihat [[lhe-on-going-rb-tw3-2025]].

## Catatan

- Sinergi: [[kepatuhan-saipi/SAIPI-65-kka-tanpa-root-cause]] (kualitas dokumentasi), [[evaluasi-spip/ESP-37-aplikasi-spip-bermasalah]].
- Rekomendasi: TIM SPIP deliver Laporan Hasil formal; integrasikan koordinasi SPIP-RB.

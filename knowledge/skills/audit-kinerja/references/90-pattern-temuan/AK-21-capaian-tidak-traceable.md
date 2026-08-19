<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/AK-21-capaian-tidak-traceable.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AK-21
skill: audit-kinerja
kategori: KINERJA-DATA
severity: MEDIUM
judul: "Capaian Kinerja Dilaporkan Tinggi tetapi Tidak Dapat Diverifikasi Sumbernya"
kriteria_baku: "SAIPI 2300 (bukti audit yang cukup, kompeten, relevan)"
tags: [data-kinerja, traceability, lkj, sumber-data, audit-kinerja]
---

# AK-21: Capaian Kinerja Dilaporkan Tinggi tetapi Tidak Dapat Diverifikasi Sumbernya

## Pattern Kondisi

Capaian kinerja/output dilaporkan tinggi, tetapi sumber data tidak dapat ditelusuri (*not traceable*). Indikator umum:

- Indikator capaian tinggi tetapi sumber data "olahan internal" tanpa referensi
- Tidak ada lampiran/sitasi/sistem sumber (aplikasi, spreadsheet, BA)
- Tidak ada analisis efisiensi (SDM, biaya) di balik capaian
- Angka capaian berbeda antar dokumen (LKj vs aplikasi vs laporan unit)

## Kriteria

SAIPI Standar 2300 — auditor harus memperoleh **bukti yang cukup, kompeten, dan relevan**. Capaian kinerja harus didukung *source of truth* yang dapat diverifikasi.

## Akibat

1. Capaian tidak dapat diyakini kewajarannya
2. Risiko klaim capaian palsu / *window dressing*
3. Penilaian AKIP/kinerja berisiko dikoreksi
4. Keputusan manajemen berbasis data tidak andal

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| LKj / Laporan Kinerja | indikator + nilai capaian |
| Lampiran/sitasi sumber | aplikasi/spreadsheet/BA pendukung |
| Aplikasi kinerja | konsistensi angka vs LKj |
| Analisis efisiensi | ada/tidak analisis SDM & biaya |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AK-21",
  "assigned_to": "{nama anggota}",
  "judul": "Capaian {indikator} {satker} Tidak Dapat Diverifikasi Sumbernya",
  "kondisi": "LKj {satker} TA {YYYY} melaporkan capaian {indikator} sebesar {X}%, namun: (a) sumber data berupa 'olahan internal' tanpa referensi; (b) tidak ada lampiran/sitasi/sistem sumber; (c) tidak ada analisis efisiensi SDM/biaya.",
  "kriteria": "SAIPI 2300 — bukti audit harus cukup, kompeten, relevan; capaian harus didukung source of truth terverifikasi.",
  "akibat": "Capaian tidak dapat diyakini; risiko klaim capaian palsu; penilaian AKIP berisiko dikoreksi.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **LHR LKj Kemkomdigi 2025** — data pendukung **tidak dapat diverifikasi sumbernya**; belum ada analisis efisiensi SDM. **LHR LKj Wasdig 2025** — SOP nomenklatur lama, belum ada Renstra/benchmark. Lihat [[lhr-lkj-kemkomdigi-2025]], [[lhr-lkj-wasdig-2025]], [[pattern-temuan]] P-35.

## Catatan

- Sinergi erat dengan [[evaluasi-sakip/ESK-34-hasil-pengukuran-belum-decision-tool]] dan [[reviu-rka-kl/RKA-02-ro-tanpa-parameter-keberhasilan]].
- Pertanyaan kunci: "Tunjukkan source of truth untuk angka capaian ini."

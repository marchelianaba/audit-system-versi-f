<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-reformasi-birokrasi/ERB-45-pelaporan-format-timeline.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ERB-45
skill: evaluasi-reformasi-birokrasi
kategori: RB-PELAPORAN
severity: MEDIUM
judul: "Pelaporan RB Format Kurang Memadai / Timeline Pelaksanaan Tidak Sesuai"
kriteria_baku: "Permenpan-RB tentang evaluasi RB (LHEI) + Road Map RB"
tags: [rb, pelaporan, lhei, timeline, renaksi, evaluasi-rb]
---

# ERB-45: Pelaporan RB Format Kurang Memadai / Timeline Tidak Sesuai

## Pattern Kondisi

Pelaporan RB belum memenuhi format yang memadai dan/atau timeline pelaksanaan rencana aksi tidak sesuai jadwal. Indikator umum:

- Format pelaporan RB kurang memadai (tidak sesuai template LHEI)
- Timeline pelaksanaan renaksi tidak sesuai jadwal yang ditetapkan
- Justifikasi perubahan rencana aksi belum didokumentasikan
- Submit LHEI ke Portal RB Nasional terlambat

## Kriteria

Permenpan-RB (evaluasi RB) — pelaporan RB (LHEI) wajib mengikuti format baku; pelaksanaan renaksi mengikuti timeline yang ditetapkan; perubahan wajib dijustifikasi.

## Akibat

1. Penilaian RB terhambat/berkurang
2. Tracking progres tidak akurat
3. Risiko nilai RB turun

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| LHEI / laporan RB | kesesuaian format template |
| Jadwal vs realisasi renaksi | ketepatan waktu |
| Justifikasi perubahan | dokumentasi alasan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ERB-45",
  "assigned_to": "{nama anggota}",
  "judul": "Pelaporan RB {satker} Format Kurang Memadai / Timeline Renaksi Tidak Sesuai",
  "kondisi": "LHE on-going RB {satker} {periode}: (a) format pelaporan kurang memadai; (b) timeline pelaksanaan renaksi tidak sesuai jadwal; (c) justifikasi perubahan rencana aksi belum didokumentasikan.",
  "kriteria": "Permenpan-RB (evaluasi RB) — pelaporan RB ikuti format baku; renaksi ikuti timeline; perubahan dijustifikasi.",
  "akibat": "Penilaian RB terhambat; tracking progres tidak akurat; risiko nilai RB turun.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **LHE on-going RB TW3 2025** — EkDig: 1 catatan pelaporan RB format kurang memadai + 1 catatan timeline pelaksanaan rencana aksi tidak sesuai (justifikasi perubahan belum didokumentasikan). Lihat [[lhe-on-going-rb-tw3-2025]], [[lhe-rb-ekosistem-digital-tw4-2025]].

## Catatan

- Rekomendasi: standarkan format LHEI; dokumentasikan justifikasi perubahan renaksi.
- Sinergi: ERB-46 (kualitas data dukung).

<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-pengadaan/PMP-54-selisih-penawaran-tanpa-kompetisi.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PMP-54
skill: pemantauan-pengadaan
kategori: PBJ-PEMILIHAN
severity: HIGH
judul: "Selisih Penawaran Signifikan Tanpa Mekanisme Kompetisi Objektif"
kriteria_baku: "Keputusan Kepala LKPP 93/2025 (E-Purchasing Katalog via Mini-Kompetisi)"
tags: [mini-kompetisi, e-katalog, kewajaran-harga, selisih-penawaran, pemantauan-pengadaan]
---

# PMP-54: Selisih Penawaran Signifikan Tanpa Mekanisme Kompetisi Objektif

## Pattern Kondisi

Penawaran yang masuk memiliki selisih harga signifikan, tetapi belum ada mekanisme kompetisi objektif untuk memastikan kewajaran harga. Indikator umum:

- Selisih penawaran besar antar penyedia (mis. Rp3,46M vs Rp2,64M)
- Salah satu penawaran belum disertai proposal teknis lengkap
- Pemilihan via e-Katalog tanpa mini-kompetisi/negosiasi
- Tidak ada metode objektif untuk memilih pemenang

## Kriteria

Keputusan Kepala LKPP **93/2025** (Lampiran I huruf A angka 3) — pemilihan via e-Katalog dengan selisih/risiko harga sebaiknya melalui **mini-kompetisi** untuk memastikan kewajaran harga (termasuk jasa konsultansi bila fitur tersedia).

## Akibat

1. Risiko ketidakwajaran harga (mark-up/under-budget)
2. Pemilihan tidak akuntabel
3. Potensi temuan/sengketa

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Rekap penawaran | selisih harga antar penyedia |
| Proposal teknis | kelengkapan per penyedia |
| Metode pemilihan | mini-kompetisi/negosiasi ada? |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PMP-54",
  "assigned_to": "{nama anggota}",
  "judul": "Selisih Penawaran {pengadaan} Signifikan (Rp{a} vs Rp{b}) Tanpa Mini-Kompetisi",
  "kondisi": "Pemantauan pengadaan {pengadaan}: penawaran {Vendor A} Rp{a} vs {Vendor B} Rp{b} (selisih signifikan); {Vendor B} belum sertakan proposal teknis lengkap. Belum ada mekanisme mini-kompetisi/negosiasi objektif.",
  "kriteria": "Kepka LKPP 93/2025 — pemilihan e-Katalog dengan selisih/risiko harga sebaiknya via mini-kompetisi untuk kewajaran harga.",
  "akibat": "Risiko ketidakwajaran harga; pemilihan tidak akuntabel; potensi temuan/sengketa.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Dutakom Rp3,46M vs Surveyor Rp2,64M ..."}]
}
```

## Contoh Kasus Historis

- **LH Monitoring Redesain TKPPSE (ND-135)** — selisih penawaran signifikan: PT Dutakom Rp3.460.000.000 (blm PPN) vs PT Surveyor Indonesia Rp2.639.673.240 (termasuk PPN); rekomendasi gunakan **mini-kompetisi e-Katalog** (Kepka LKPP 93/2025). Lihat [[nota-dinas-ir2-mei-2026]] (ND-135).

## Catatan

- Sinergi: [[reviu-pengadaan/RP-15-e-katalog-tanpa-negosiasi]], [[konsultasi-pengadaan/KSP-57-e-katalog-tanpa-mini-kompetisi]].
- Rekomendasi: gunakan mini-kompetisi/negosiasi sebelum penetapan pemenang.

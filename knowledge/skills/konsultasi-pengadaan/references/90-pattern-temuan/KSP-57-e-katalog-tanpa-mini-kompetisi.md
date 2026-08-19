<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/konsultasi-pengadaan/KSP-57-e-katalog-tanpa-mini-kompetisi.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: KSP-57
skill: konsultasi-pengadaan
kategori: PBJ-PEMILIHAN
severity: MEDIUM
judul: "E-Katalog Tanpa Mini-Kompetisi untuk Nilai Signifikan"
kriteria_baku: "Keputusan Kepala LKPP 93/2025 (E-Purchasing via Mini-Kompetisi)"
tags: [e-katalog, mini-kompetisi, advisory, kewajaran-harga, konsultasi-pengadaan]
---

# KSP-57: E-Katalog Tanpa Mini-Kompetisi untuk Nilai Signifikan

## Pattern Kondisi

Saat memberikan konsultasi pra-pengadaan, ditemukan rencana pemilihan via e-Katalog tanpa mini-kompetisi untuk nilai signifikan/beberapa penyedia tersedia. Indikator umum:

- Nilai pengadaan signifikan tetapi rencana *e-purchasing* langsung (tanpa kompetisi)
- Tersedia >1 penyedia di katalog tetapi tidak dikompetisikan
- Selisih harga antar penyedia potensial belum diuji
- Belum mempertimbangkan mini-kompetisi padahal fitur tersedia

## Kriteria

Keputusan Kepala LKPP **93/2025** — E-Purchasing Katalog untuk nilai/risiko tertentu sebaiknya melalui **mini-kompetisi** guna memastikan kewajaran harga (termasuk jasa konsultansi bila fitur tersedia).

## Akibat

1. Risiko harga tidak kompetitif
2. Audit trail kewajaran harga lemah
3. Potensi temuan pasca-pengadaan

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Rencana pemilihan | metode e-purchasing langsung vs mini-kompetisi |
| Ketersediaan penyedia di katalog | jumlah penyedia |
| Nilai paket | signifikansi nilai |

## Format Temuan / Catatan Advisory (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-KSP-57",
  "assigned_to": "{nama anggota}",
  "judul": "Rencana E-Katalog {paket} Tanpa Mini-Kompetisi untuk Nilai Signifikan",
  "kondisi": "Konsultasi pra-pengadaan {paket} Rp{X}: rencana e-purchasing langsung meskipun tersedia >1 penyedia di katalog dan nilai signifikan; mini-kompetisi belum dipertimbangkan.",
  "kriteria": "Kepka LKPP 93/2025 — E-Purchasing Katalog untuk nilai/risiko tertentu sebaiknya via mini-kompetisi untuk kewajaran harga.",
  "akibat": "Risiko harga tidak kompetitif; audit trail kewajaran harga lemah; potensi temuan pasca-pengadaan.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **ST-90 Konsultasi HPS/Mini-Kompetisi E-Katalog DJED (12-14 Mei 2026)** + **ND-135 LH Monitoring Redesain TKPPSE** — IR II merekomendasikan mekanisme **mini-kompetisi e-Katalog** (Kepka LKPP 93/2025) untuk menghindari risiko ketidakwajaran harga. Lihat [[surat-tugas-ir2-mei-2026]], [[nota-dinas-ir2-mei-2026]] (ND-135).

## Catatan

- Sebagai advisory pra-pengadaan, sampaikan sebagai **masukan** (bukan temuan) bila proses belum berjalan.
- Sinergi: [[pemantauan-pengadaan/PMP-54-selisih-penawaran-tanpa-kompetisi]], [[reviu-pengadaan/RP-15-e-katalog-tanpa-negosiasi]].

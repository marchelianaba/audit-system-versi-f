<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-tindak-lanjut/PTL-50-verifikasi-outstanding-belum-tuntas.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PTL-50
skill: pemantauan-tindak-lanjut
kategori: TLHP-FINANSIAL
severity: HIGH
judul: "Verifikasi Outstanding Finansial Belum Tuntas (Scope Gap)"
kriteria_baku: "Mandat BPK + SAIPI 2300 (cakupan verifikasi sesuai mandat)"
tags: [tlhp, verifikasi, jar, scope-gap, outstanding-finansial, pemantauan-tl]
---

# PTL-50: Verifikasi Outstanding Finansial Belum Tuntas (Scope Gap)

## Pattern Kondisi

BPK meminta verifikasi total atas nilai outstanding, tetapi reviu/verifikasi APIP belum mencakup seluruh mandat (ada *scope gap*). Indikator umum:

- BPK minta verifikasi total Rp{X}, reviu APIP belum lengkap
- Sebagian lokasi/site terlewat dari verifikasi (mis. 3 site Rp3,15M)
- Laporan Hasil Verifikasi belum disampaikan/selesai
- Rekomendasi TL hasil reviu belum ditindaklanjuti unit operasional

## Kriteria

Mandat BPK + SAIPI Standar 2300 — verifikasi APIP wajib mencakup seluruh ruang lingkup yang diminta BPK; cakupan tidak boleh kurang dari mandat.

## Akibat

1. Outstanding finansial tidak dapat dituntaskan
2. Rekomendasi BPK tetap "Belum Sesuai"
3. Nilai tidak dapat diyakini sebagian

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Surat permintaan BPK | nilai + scope yang diminta |
| Laporan Hasil Verifikasi APIP | cakupan vs mandat |
| Daftar site/objek | yang terlewat verifikasi |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PTL-50",
  "assigned_to": "{nama anggota}",
  "judul": "Verifikasi {objek} Rp{X} Belum Tuntas — Scope Gap {Y}",
  "kondisi": "BPK meminta verifikasi total {objek} Rp{X}; reviu APIP belum mencakup {N} site senilai Rp{Y}; Laporan Hasil Verifikasi belum {selesai/disampaikan}; rekomendasi TL belum ditindaklanjuti {unit}.",
  "kriteria": "Mandat BPK + SAIPI 2300 — verifikasi APIP wajib mencakup seluruh ruang lingkup yang diminta BPK.",
  "akibat": "Outstanding finansial tidak tuntas; rekomendasi BPK tetap Belum Sesuai; nilai tidak dapat diyakini sebagian.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "JAR Rp171,59M; kurang 3 site Rp3,15M ..."}]
}
```

## Contoh Kasus Historis

- **TLRHP BPK Semester II 2025 / TLHP Eksternal Simwas** — JAR TA 2022-2024 senilai **Rp171,59M** belum sepenuhnya diverifikasi; Itjen belum selesai reviu untuk **3 site Rp3,15M**; verifikasi bukti tagihan OM TKPPSE Rp16,56M belum disampaikan. Lihat [[tlrhp-bpk-semester-2-2025]], [[tlhp-eksternal-simwas-ir2]], [[pattern-temuan]] P-27. Pasangan eksekusi: ST-96 cek fisik JAR ([[surat-tugas-ir2-mei-2026]]).

## Catatan

- Rekomendasi: lengkapi reviu sesuai mandat BPK (no gap); SK PIC definitif di unit penerus.
- Sinergi: PTL-51 (ownership pasca-SOTK), [[audit-pengadaan/AP-25-data-prestasi-tidak-memadai]].

<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/konsultasi-pengadaan/KSP-59-itjen-advisor-pra-pengadaan.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: KSP-59
skill: konsultasi-pengadaan
kategori: PBJ-ADVISORY
severity: INFO
judul: "Itjen Dilibatkan sebagai Advisor Pra-Pengadaan (Good Practice)"
kriteria_baku: "SAIPI 2010 (consulting activity) + Renstra 3.2.1 pre-audit approach"
tags: [advisory, consulting, pre-audit, good-practice, konsultasi-pengadaan]
---

# KSP-59: Itjen Dilibatkan sebagai Advisor Pra-Pengadaan (Good Practice)

## Pattern Kondisi

Inspektorat dilibatkan mitra sejak tahap perencanaan/penyusunan HPS pengadaan — sebuah **good practice** *pre-audit/consulting* yang perlu didokumentasikan + dijaga independensinya. Indikator umum:

- IR II diundang sebagai narasumber/reviewer HPS oleh mitra (bukan auditor pemeriksa)
- Keterlibatan pada tahap perencanaan (sebelum pemilihan)
- Peran konsultatif/advisory, bukan assurance
- Potensi *self-review threat* bila kelak mengaudit paket yang sama

## Kriteria

SAIPI Standar **2010** (sifat penugasan consulting) + strategi Renstra 3.2.1 (pengawasan terintegrasi sejak perencanaan) — APIP dapat memberikan consulting; wajib menjaga **independensi** & mencatat keterlibatan agar tidak menimbulkan *self-review threat* saat assurance.

## Akibat / Pertimbangan

1. (Positif) Pencegahan dini lebih efektif dari audit post-hoc
2. (Risiko) *Self-review threat* bila kelak mengaudit paket yang sama
3. Perlu dokumentasi peran + batasan tanggung jawab APIP

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Surat undangan mitra | peran IR II (narasumber/reviewer) |
| ST penugasan | klasifikasi consulting vs audit |
| Dokumentasi masukan advisory | batasan tanggung jawab tercatat |

## Format Catatan (untuk diisi agen ke `append_temuan` — kategori INFO/good practice)

```json
{
  "sasaran_id": "S-KSP-59",
  "assigned_to": "{nama anggota}",
  "judul": "Keterlibatan Advisory IR II pada Pra-Pengadaan {paket} (Good Practice)",
  "kondisi": "IR II dilibatkan sebagai advisor/reviewer HPS {paket} pada tahap perencanaan (ST {nomor}). Peran konsultatif (bukan assurance). Perlu dokumentasi batasan tanggung jawab + mitigasi self-review threat untuk audit paket yang sama di masa depan.",
  "kriteria": "SAIPI 2010 (consulting) + Renstra 3.2.1 — APIP dapat consulting; wajib jaga independensi & catat keterlibatan.",
  "akibat": "Pencegahan dini efektif; namun perlu mitigasi self-review threat + dokumentasi batasan tanggung jawab APIP.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Undangan B-4195/DJED.6 konsultasi teknis HPS ..."}]
}
```

## Contoh Kasus Historis

- **ST-90 (12-14 Mei 2026)** — Muhammad Arief (Inspektur II) hadir solo sebagai narasumber/reviewer HPS pada konsultasi teknis DJED.6 (Dit. Pengendalian Ekosistem Digital) — *pre-audit approach*. Lihat [[surat-tugas-ir2-mei-2026]] (ST-90), [[renstra-itjen-2025-2029]] (3.2.1).

## Catatan

- Bukan temuan negatif; dokumentasikan sebagai good practice + catat mitigasi independensi.
- Sinergi: [[kepatuhan-saipi/README]] (independensi SAIPI 1100).

<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/AK-20-layanan-baru-lemah-tatakelola.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AK-20
skill: audit-kinerja
kategori: KINERJA-TATAKELOLA
severity: HIGH
judul: "Layanan Baru Diluncurkan dengan Kelemahan Tata Kelola Hulu + Keamanan Hilir"
kriteria_baku: "UU 27/2022 PDP + tata kelola SPBE + SAIPI 2200"
tags: [layanan-baru, igrs, tata-kelola, keamanan-data, klasifikasi, audit-kinerja]
---

# AK-20: Layanan Baru Diluncurkan dengan Kelemahan Tata Kelola Hulu + Keamanan Hilir

## Pattern Kondisi

Sistem/layanan baru diluncurkan dengan kelemahan tata kelola di hulu (klasifikasi/verifikasi/standar) dan kelemahan keamanan di hilir (API terbuka, data sensitif terekspos). Indikator umum:

- Inkonsistensi hasil klasifikasi/rating antar-penilai
- Mekanisme keberatan/koreksi (mis. *Rating Change*) tidak transparan
- Kebocoran/eksposur data pengguna/pengembang
- Layanan *go-live* tanpa *acceptance testing* publik atau *pen-test* keamanan
- Tata kelola kemitraan (peran pihak ketiga) belum jelas

## Kriteria

UU 27/2022 Pelindungan Data Pribadi + prinsip tata kelola SPBE + SAIPI 2200 — layanan publik berbasis sistem elektronik harus memenuhi standar tata kelola, akurasi, dan keamanan data sebelum dan selama operasional.

## Akibat

1. Hasil layanan tidak dapat dipercaya (rating tidak konsisten)
2. Risiko hukum PDP atas kebocoran data
3. Sengketa dengan pemangku kepentingan (industri/publik)
4. Reputasi Kementerian menurun

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| SOP klasifikasi/rating | konsistensi kriteria antar-penilai |
| Mekanisme RC/keberatan | transparansi + jejak keputusan |
| Hasil uji keamanan/API | eksposur data sensitif |
| BA UAT/pen-test pra-launch | ada/tidak |

**Framework reusable 5 area** (dari sasaran audit IGRS): (1) kesiapan sistem, (2) akurasi klasifikasi, (3) mekanisme RC, (4) keamanan, (5) tata kelola kemitraan.

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AK-20",
  "assigned_to": "{nama anggota}",
  "judul": "Layanan {nama} Beroperasi dengan Kelemahan Tata Kelola & Keamanan",
  "kondisi": "Layanan {nama} TA {YYYY}: (a) inkonsistensi {rating/klasifikasi} antar-penilai; (b) mekanisme {RC/keberatan} tidak transparan; (c) {kebocoran/eksposur} data {pengguna/pengembang}; (d) tidak ada bukti UAT publik / pen-test pra-launch.",
  "kriteria": "UU 27/2022 PDP + tata kelola SPBE + SAIPI 2200 — layanan elektronik harus memenuhi standar tata kelola, akurasi, dan keamanan data.",
  "akibat": "Hasil layanan tidak dapat dipercaya; risiko hukum PDP; sengketa pemangku kepentingan; reputasi menurun.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **Audit Kinerja Layanan Klasifikasi Gim / IGRS (ST-92)** — 3 isu kritis: inkonsistensi rating, status *Rating Change* tidak transparan, kebocoran data developer. Sasaran audit memakai framework 5 area. Lihat [[isu-igrs]], [[sasaran-audit-igrs]], [[pattern-temuan]] P-30.

## Catatan

- Framework 5 area IGRS **reusable** untuk audit layanan baru K/L lain.
- Rekomendasi: UAT publik + *security pen-test* sebagai prasyarat *go-live*.

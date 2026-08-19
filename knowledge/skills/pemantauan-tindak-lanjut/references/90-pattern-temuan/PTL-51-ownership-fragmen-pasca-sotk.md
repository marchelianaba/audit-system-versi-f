<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-tindak-lanjut/PTL-51-ownership-fragmen-pasca-sotk.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PTL-51
skill: pemantauan-tindak-lanjut
kategori: TLHP-OWNERSHIP
severity: HIGH
judul: "Ownership Rekomendasi Fragmen Pasca-Likuidasi/SOTK"
kriteria_baku: "Pedoman Pemantauan TLHP + ketentuan SOTK (PM Komdigi 1/2025)"
tags: [tlhp, ownership, aptaka, likuidasi, sotk, warisan-rekomendasi, pemantauan-tl]
---

# PTL-51: Ownership Rekomendasi Fragmen Pasca-Likuidasi/SOTK

## Pattern Kondisi

Rekomendasi warisan unit yang dilikuidasi/direstrukturisasi (SOTK) kehilangan kepemilikan yang jelas. Indikator umum:

- Rekomendasi >2 tahun belum ditangani karena PPK/PIC lama pindah unit
- Tidak ada SK PIC baru untuk rekomendasi warisan
- Ownership fragmen antar unit penerus (mis. JAR + HUB.ID dari Aptaka)
- Outstanding finansial warisan menggantung

## Kriteria

Pedoman Pemantauan TLHP + ketentuan SOTK — setiap rekomendasi outstanding wajib punya PIC yang jelas; saat SOTK/likuidasi, kepemilikan rekomendasi wajib dialihkan formal ke unit penerus.

## Akibat

1. Rekomendasi warisan menggantung tanpa penanggung jawab
2. Outstanding finansial tidak tertangani (mis. Rp30,27M)
3. Akuntabilitas TL terputus

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Rekap TLHP warisan | rekomendasi unit yang dilikuidasi |
| SK PIC/penanggung jawab | ada/tidak penetapan baru |
| Mapping unit lama → penerus | kejelasan pengalihan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PTL-51",
  "assigned_to": "{nama anggota}",
  "judul": "Ownership Rekomendasi Warisan {unit lama} Fragmen — Rp{X} Menggantung",
  "kondisi": "Rekomendasi warisan {unit lama} (mis. {JAR Rp.., HUB.ID Rp..}) belum ditangani >2 tahun: PPK era lama pindah unit; tidak ada SK PIC baru; ownership fragmen antara {unit penerus A} dan {unit penerus B}. Outstanding finansial Rp{X}.",
  "kriteria": "Pedoman Pemantauan TLHP + ketentuan SOTK — rekomendasi outstanding wajib punya PIC jelas; saat SOTK kepemilikan dialihkan formal ke unit penerus.",
  "akibat": "Rekomendasi warisan menggantung; outstanding finansial tidak tertangani; akuntabilitas TL terputus.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "JAR Rp27,6M + HUB.ID Rp2,66M warisan Aptaka ..."}]
}
```

## Contoh Kasus Historis

- **TLHP Internal Simwas IR2** — outstanding finansial **Rp30,27M** lintas satker (TKPPSE + JAR Aptaka + HUB.ID Startup); ownership fragmen pasca-likuidasi Aptaka → EkDig/Wasdig; PPK era Aptaka pindah unit. Lihat [[tlhp-internal-simwas-ir2]], [[pemantauan-tlhp-ekdig-2025]], [[pattern-temuan]] P-24.

## Catatan

- Rekomendasi: SK definitif PIC untuk setiap rekomendasi warisan; eskalasi ke Irjen jika tidak ada PIC dalam 3 bulan pasca-SOTK.
- Sinergi: PTL-50 (verifikasi JAR), [[evaluasi-spip/README]] (transisi SOTK).

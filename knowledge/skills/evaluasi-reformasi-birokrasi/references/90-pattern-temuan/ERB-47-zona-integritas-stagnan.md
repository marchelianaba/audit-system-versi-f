<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-reformasi-birokrasi/ERB-47-zona-integritas-stagnan.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ERB-47
skill: evaluasi-reformasi-birokrasi
kategori: RB-ZI
severity: HIGH
judul: "Pembangunan Zona Integritas Stagnan Lintas Tahun"
kriteria_baku: "Permenpan-RB 90/2021 tentang Pembangunan ZI menuju WBK/WBBM"
tags: [rb, zona-integritas, wbk, wbbm, stagnan, permenpanrb-90]
---

# ERB-47: Pembangunan Zona Integritas Stagnan Lintas Tahun

## Pattern Kondisi

Pembangunan Zona Integritas (ZI) menuju WBK/WBBM tidak berkembang selama beberapa tahun. Indikator umum:

- Persentase unit ber-ZI flat lintas tahun (mis. 16,67% / 1 dari 6 unit, 2 tahun)
- Komitmen pimpinan belum penuh
- Mekanisme reward/punishment ZI belum efektif
- Tim Penilai Internal (TPI) tidak diregenerasi/aktif tahunan

## Kriteria

Permenpan-RB 90/2021 — pembangunan ZI menuju WBK/WBBM merupakan bagian RB; instansi diharapkan menambah unit ber-predikat WBK/WBBM secara progresif.

## Akibat

1. Budaya antikorupsi/pelayanan prima tidak menyebar
2. Nilai RB komponen ZI tertahan
3. Indikator paling problematik di LKE PAN-RB

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| LKE RB (komponen ZI) | % unit ZI lintas tahun |
| SK Tim Penilai Internal (TPI) | aktif & diregenerasi? |
| Survei integritas pasca-pencanangan | hasil surveillance |
| Acceleration plan ZI | ada/tidak |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ERB-47",
  "assigned_to": "{nama anggota}",
  "judul": "Pembangunan Zona Integritas Stagnan {X}% Selama {N} Tahun",
  "kondisi": "LKE RB {periode}: persentase unit ber-ZI flat {X}% ({a} dari {b} unit) selama {N} tahun. Komitmen pimpinan belum penuh; mekanisme reward/punishment belum efektif; TPI belum diregenerasi.",
  "kriteria": "Permenpan-RB 90/2021 — pembangunan ZI menuju WBK/WBBM bagian RB; instansi diharapkan menambah unit ber-predikat progresif.",
  "akibat": "Budaya antikorupsi/pelayanan prima tidak menyebar; nilai RB komponen ZI tertahan.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "ZI 16,67% flat 2 tahun ..."}]
}
```

## Contoh Kasus Historis

- **LKE RB Kemkomdigi 2024–2025** — pembangunan ZI stuck di **16,67%** (1 dari 6 unit) selama 2 tahun berturut-turut. Lihat [[lke-rb-kemkomdigi-2024-2025]], [[penilaian-internal-zi-2026]], [[pattern-temuan]] P-34.

## Catatan

- Rekomendasi: akselerasi via SK TPI baru (ND-130 Tim Penilai Internal ZI 2026) + mekanisme insentif.
- Sinergi: terkait IEPK ([[kepatuhan-saipi/SAIPI-64-register-risiko-fraud-belum-ada]]).

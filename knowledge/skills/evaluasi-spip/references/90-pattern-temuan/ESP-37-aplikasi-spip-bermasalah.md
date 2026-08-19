<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-spip/ESP-37-aplikasi-spip-bermasalah.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESP-37
skill: evaluasi-spip
kategori: SPIP-SISTEM
severity: MEDIUM
judul: "Aplikasi SPIP Bermasalah / Kertas Kerja Tidak Terisi"
kriteria_baku: "Perka BPKP 5/2021 (penyelenggaraan & dokumentasi SPIP)"
tags: [spip, aplikasi, kertas-kerja, kk-lead, sistem-informasi, perka-bpkp-5]
---

# ESP-37: Aplikasi SPIP Bermasalah / Kertas Kerja Tidak Terisi

## Pattern Kondisi

Aplikasi/sistem informasi SPIP mengalami kendala teknis atau kertas kerja penilaian tidak terisi, sehingga siklus penilaian mandiri terhambat. Indikator umum:

- Aplikasi SPIP bermasalah secara teknis
- Sebagian besar Kertas Kerja (mis. KK Lead II) belum/tidak terisi (mis. 7 dari 13 KK)
- Pengisian penilaian mandiri 0% pada beberapa unit pada periode tertentu
- Siklus penilaian terancam mundur akibat sistem

## Kriteria

Perka BPKP 5/2021 — penyelenggaraan SPIP didokumentasikan dalam kertas kerja yang lengkap; sistem informasi pendukung harus berfungsi memadai untuk mendukung penilaian.

## Akibat

1. Penilaian maturitas tidak dapat dilakukan tepat waktu
2. Data risiko/pengendalian tidak lengkap
3. Skor maturitas berisiko turun karena bukti tidak terdokumentasi

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Aplikasi SPIP | status fungsional + kendala teknis |
| Kertas Kerja (Lead/parameter) | persentase terisi |
| Progres pengisian per unit | unit dengan 0% pengisian |
| Timeline penilaian mandiri | risiko mundur |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESP-37",
  "assigned_to": "{nama anggota}",
  "judul": "Aplikasi SPIP Bermasalah / {M} dari {N} Kertas Kerja {satker} Belum Terisi",
  "kondisi": "Penilaian mandiri SPIP {satker} {periode}: aplikasi SPIP bermasalah teknis; {M} dari {N} kertas kerja (mis. KK Lead II) belum terisi; {unit} 0% pengisian. Siklus penilaian terancam mundur.",
  "kriteria": "Perka BPKP 5/2021 — penyelenggaraan SPIP didokumentasikan dalam kertas kerja lengkap; sistem informasi pendukung harus berfungsi memadai.",
  "akibat": "Penilaian maturitas tidak tepat waktu; data risiko/pengendalian tidak lengkap; skor berisiko turun.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "7 dari 13 KK belum terisi; KK Lead II 0/4 ..."}]
}
```

## Contoh Kasus Historis

- **Atensi Progres SPIP & MR 2025** — SPIP Tingkat Kementerian: 7 dari 13 kertas kerja belum terisi; **KK Lead II seluruh 4 kosong** (inti penilaian maturitas); aplikasi SPIP Kemkomdigi bermasalah teknis. Lihat [[atensi-progres-spip-mr-2025]], [[pattern-temuan]] P-28.

## Catatan

- Rekomendasi: stabilkan aplikasi SPIP; tetapkan PIC + deadline pengisian KK.
- Sinergi: [[evaluasi-manajemen-risiko/EMR-39-pemantauan-belum-diinput]] (pola pengisian sistem sama).

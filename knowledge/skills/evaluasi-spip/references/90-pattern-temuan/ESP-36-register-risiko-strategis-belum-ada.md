<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-spip/ESP-36-register-risiko-strategis-belum-ada.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESP-36
skill: evaluasi-spip
kategori: SPIP-MR
severity: HIGH
judul: "Register Risiko Strategis & Rencana Tindak Pengendalian Belum Ada/Dikomunikasikan"
kriteria_baku: "PP 60/2008 + Perka BPKP 5/2021 (area Manajemen Risiko Indeks/MRI)"
tags: [spip, mri, register-risiko, rtp, risiko-strategis, perka-bpkp-5]
---

# ESP-36: Register Risiko Strategis & RTP Belum Ada/Dikomunikasikan

## Pattern Kondisi

Manajemen risiko tingkat strategis belum dikelola memadai dalam kerangka SPIP. Indikator umum:

- Register risiko strategis belum ada / belum lengkap
- Rencana Tindak Pengendalian (RTP) tingkat strategis belum dikomunikasikan ke seluruh pihak
- Reviu berkala kebijakan MR belum dilakukan
- Kompetensi MR pegawai belum merata (lihat ESP-38)

## Kriteria

PP 60/2008 + Perka BPKP 5/2021 (area **MRI**) — penyelenggaraan SPIP mensyaratkan identifikasi & penanganan risiko strategis terdokumentasi (register risiko + RTP) dan dikomunikasikan.

## Akibat

1. Risiko strategis tidak terkelola aktif
2. Skor MRI turun saat penjaminan (lihat ESP-35)
3. Pengendalian tidak terarah pada risiko prioritas

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Register risiko strategis | ada/lengkap/terkini |
| RTP tingkat strategis | ada + dikomunikasikan |
| Bukti reviu kebijakan MR | reviu berkala dilakukan? |
| Catatan AoI penjaminan | dominasi isu MR strategis |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESP-36",
  "assigned_to": "{nama anggota}",
  "judul": "Register Risiko Strategis & RTP {satker} Belum Ada/Dikomunikasikan",
  "kondisi": "Penjaminan kualitas SPIP {satker}: (a) register risiko strategis belum {ada/lengkap}; (b) RTP tingkat strategis belum dikomunikasikan ke seluruh pihak; (c) reviu berkala kebijakan MR belum dilakukan. {N} catatan AoI dominan isu MR strategis.",
  "kriteria": "PP 60/2008 + Perka BPKP 5/2021 (area MRI) — risiko strategis wajib teridentifikasi, ditangani (register + RTP), dan dikomunikasikan.",
  "akibat": "Risiko strategis tidak terkelola aktif; skor MRI turun; pengendalian tidak terarah pada risiko prioritas.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "10 AoI dominan MR strategis ..."}]
}
```

## Contoh Kasus Historis

- **Laporan Penjaminan Kualitas SPIP Kemkomdigi Final 2025** — 10 AoI dominan isu **MR strategis** (penetapan prioritas risiko strategis, kompetensi MR pegawai, komunikasi strategi MR). **Penjaminan Kualitas SPIP Ekdig** — register risiko + RTP tingkat strategis belum dikomunikasikan ke seluruh pihak. Lihat [[laporan-penjaminan-kualitas-spip-kemkomdigi-final-2025]], [[penjaminan-kualitas-spip-ekdig-final-2025]].

## Catatan

- Sinergi kuat dengan [[evaluasi-manajemen-risiko/EMR-41-rencana-penanganan-belum-diisi]] (MR & SPIP saling memperkuat).
- Rekomendasi: susun register risiko strategis + RTP + komunikasikan; jadwalkan reviu kebijakan MR berkala.

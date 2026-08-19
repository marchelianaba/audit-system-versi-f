<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-pengadaan/PMP-53-jawaban-rfi-belum-lengkap.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PMP-53
skill: pemantauan-pengadaan
kategori: PBJ-RFI
severity: HIGH
judul: "Jawaban RFI Belum Lengkap Menghambat Target Pengadaan"
kriteria_baku: "Perpres 16/2018 Pasal 18 (perencanaan pengadaan)"
tags: [rfi, pengadaan, redesain-tkppse, progres, pemantauan-pengadaan]
---

# PMP-53: Jawaban RFI Belum Lengkap Menghambat Target Pengadaan

## Pattern Kondisi

Request for Information (RFI) dikirim ke beberapa calon penyedia, tetapi jawaban yang masuk minim sehingga mempersempit pilihan & menghambat target pengadaan. Indikator umum:

- Hanya sebagian kecil penerima RFI menjawab (mis. 2 dari 6)
- Penyedia akademisi/vendor belum merespons mendekati target pengadaan
- Hanya 1-2 penawaran harga formal yang masuk
- Target jadwal pengadaan berisiko mundur

## Kriteria

Perpres 16/2018 Pasal 18 (perencanaan pengadaan) — penjajakan pasar/RFI harus memadai untuk memastikan ketersediaan penyedia & kewajaran harga sebelum pemilihan.

## Akibat

1. Pilihan calon penyedia menyempit (risiko persaingan rendah)
2. Target jadwal pengadaan mundur
3. Kewajaran harga sulit divalidasi (lihat PMP-54)

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Daftar penerima RFI + status | berapa menjawab vs dikirim |
| Surat RFI + tanggal | timeline pengiriman vs target |
| Jawaban RFI | kelengkapan (harga + teknis) |
| Target jadwal pengadaan | risiko mundur |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PMP-53",
  "assigned_to": "{nama anggota}",
  "judul": "Hanya {a} dari {b} Penerima RFI {pengadaan} yang Menjawab",
  "kondisi": "Pemantauan progres pengadaan {pengadaan}: RFI dikirim ke {b} pihak ({akademisi}+{vendor}); baru {a} menjawab ({nama}), {c} belum. Target pengadaan {bulan} berisiko mundur; pilihan penyedia menyempit.",
  "kriteria": "Perpres 16/2018 Pasal 18 — penjajakan pasar/RFI harus memadai untuk memastikan ketersediaan penyedia & kewajaran harga.",
  "akibat": "Pilihan calon penyedia menyempit; target jadwal mundur; kewajaran harga sulit divalidasi.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "2 dari 6 penerima RFI menjawab ..."}]
}
```

## Contoh Kasus Historis

- **LH Monitoring Redesain TKPPSE (ND-135, output ST-81)** — RFI dikirim ke 6 pihak (2 akademisi + 4 vendor); baru **2 menjawab** (PT Dutakom Rp3,46M, PT Surveyor Indonesia Rp2,64M); STEI ITB, Pusilkom UI, Sisindokom, Berca belum. Target pengadaan Jun-Jul 2026 berisiko. Lihat [[nota-dinas-ir2-mei-2026]] (ND-135).

## Catatan

- Rekomendasi: *follow-up* penerima RFI yang belum menjawab agar pengadaan tepat waktu.
- Sinergi: PMP-54 (selisih harga → mini-kompetisi), [[reviu-pengadaan/RP-08-hps-rfi-minimum]].

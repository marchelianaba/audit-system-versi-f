<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/AK-18-hasil-deteksi-tidak-ditindaklanjuti.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AK-18
skill: audit-kinerja
kategori: KINERJA-PROSES
severity: HIGH
judul: "Hasil Deteksi/Crawling Tidak Ditindaklanjuti Sampai Tuntas"
kriteria_baku: "SAIPI 2300 + SOP penanganan konten/aduan + UU 1/2024 ITE"
tags: [crawling, cse, proses-bisnis, tindak-lanjut, verifikator, audit-kinerja]
---

# AK-18: Hasil Deteksi/Crawling Tidak Ditindaklanjuti Sampai Tuntas

## Pattern Kondisi

Sistem deteksi menghasilkan volume temuan besar, tetapi proses bisnis hilir (verifikasi → validasi → serah terima → tindak lanjut → closure) tidak berjalan tuntas/akuntabel. Indikator umum:

- Jutaan hasil *crawling* belum diverifikasi/ditindaklanjuti (mis. 3.839.549 hasil)
- *Keyword management* lemah; verifikator tidak independen/tidak seragam
- Tidak ada *audit trail* status tiap item (terdeteksi → diblokir → selesai)
- Pemblokiran terlambat; daftar hitam tidak sinkron antar sistem
- Tidak ada KPI penyelesaian (SLA waktu tindak lanjut)

## Kriteria

SAIPI Standar 2300 (Pelaksanaan Penugasan) — proses bisnis harus dapat ditelusuri end-to-end dengan bukti memadai; SOP penanganan konten + UU 1/2024 ITE mengamanatkan pengendalian konten yang melanggar dilakukan secara akuntabel dan tuntas.

## Akibat

1. Tujuan deteksi tidak berdampak (konten tetap beredar)
2. Beban kerja menumpuk; backlog tidak terukur
3. Sulit pertanggungjawaban — tidak ada bukti penyelesaian per item
4. Temuan BPK berulang atas efektivitas penanganan

## Bukti Yang Harus Dicari

| Dokumen | Section / Field | Yang dicari |
|---------|-----------------|-------------|
| Log sistem crawling | jumlah & status item | total terdeteksi vs ditindaklanjuti |
| SOP verifikasi/validasi | alur + PIC | independensi verifikator, tahapan |
| BA serah terima daftar hitam | tanggal + jumlah | sinkronisasi ke sistem pemblokiran |
| KPI/SLA tindak lanjut | target waktu | ada/tidak target penyelesaian |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AK-18",
  "assigned_to": "{nama anggota}",
  "judul": "{N} Hasil Crawling {sistem} Belum Ditindaklanjuti Sampai Tuntas",
  "kondisi": "Sistem {sistem} menghasilkan {N} item terdeteksi TA {YYYY}; pemeriksaan menemukan: (a) {M} item belum diverifikasi/ditindaklanjuti; (b) keyword management lemah & verifikator tidak independen; (c) tidak ada audit trail status per item; (d) tidak ada SLA waktu tindak lanjut.",
  "kriteria": "SAIPI 2300 + SOP penanganan konten + UU 1/2024 ITE — proses bisnis harus tertelusur end-to-end dan tuntas secara akuntabel.",
  "akibat": "Tujuan deteksi tidak berdampak; backlog menumpuk tak terukur; pertanggungjawaban lemah; temuan BPK berulang.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "3.839.549 hasil crawling ..."}]
}
```

## Contoh Kasus Historis

- **LHP Kinerja BPK PSTE 2024** — **3.839.549 hasil crawling CSE belum ditindaklanjuti**; keyword management lemah, verifikator tidak independen, pemblokiran terlambat; pendistribusian daftar hitam tidak sinkron dengan batch list sumber. Lihat [[bpk-kinerja-pste-2024]] + [[lhr-server-crawling-2025]].

## Catatan

- Pertanyaan kunci agen: "Dari N item terdeteksi, berapa yang berstatus selesai dan apa buktinya?"
- Sinergi: AK-19 (tumpang tindih CNS/CSE), [[pattern-temuan]] P-25 (TLHP struktural konten).

<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-umum/pm-02-02-konsistensi-data.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PM-02
skill: pemantauan-umum
kategori: KONSISTENSI-DATA
severity: LOW
judul: "Inkonsistensi Data antar Dokumen Pendukung"
kriteria_baku: "Prinsip keterhubungan data (data integrity) — antar dokumen objek pengawasan"
tags: ['konsistensi', 'data', 'integritas-dokumen']
starter: true
---

# PM-02: Inkonsistensi Data antar Dokumen Pendukung

## Pattern Kondisi
Data antar dokumen objek pengawasan Pemantauan tidak konsisten — angka, tanggal, nama pihak, atau referensi pasal berbeda di dokumen yg seharusnya saling rujuk. Indikator umum:
- Nilai anggaran di dokumen A ≠ dokumen B (mis. SPM vs BAST)
- Tanggal di header ≠ tanggal yang dirujuk di paragraf
- Nama pihak (pejabat, vendor, unit kerja) berbeda format/ejaan
- Pasal regulasi yg dirujuk berbeda antara KAK vs dokumen evaluasi

## Kriteria
- Permenpan RB tentang Akuntabilitas Kinerja — keselarasan dokumen kinerja
- Permenkeu/Perpres pengadaan — keselarasan dokumen perencanaan & pelaksanaan
- Per jenis: konsistensi vertikal sasaran → KPI → bukti

## Akibat
- Temuan auditor jadi sulit di-trace ke sumber kebenaran
- Risiko misleading: kesimpulan auditor salah karena dasar inkonsisten
- Reputasi auditi tergerus saat dokumen ditelaah eksternal (BPK)

## Sebab Umum
- Penyusunan dokumen di unit kerja berbeda tanpa cross-check
- Versi dokumen tidak terkontrol (multiple draft beredar)
- Tidak ada single source of truth untuk angka kunci

## Rekomendasi Pattern
- Unit kerja punya register dokumen + versi kontrol
- Field kunci (anggaran, tanggal, pasal) di-cross-check sebelum dokumen final
- Auditor merekomendasikan SOP konsolidasi dokumen pasca-revisi

## Catatan
Pattern starter — lihat pattern 01 untuk konteks deprekasi.

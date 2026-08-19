<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-umum/ev-01-01-kelengkapan-dokumen.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: EV-01
skill: evaluasi-umum
kategori: KELENGKAPAN-DOKUMEN
severity: MEDIUM
judul: "Kelengkapan Dokumen Pendukung Belum Memadai"
kriteria_baku: "SOP Pengawasan APIP + standar pendokumentasian per jenis pengawasan"
tags: ['kelengkapan', 'dokumen', 'standar-pendokumentasian']
starter: true
---

# EV-01: Kelengkapan Dokumen Pendukung Belum Memadai

## Pattern Kondisi
Dokumen pendukung penugasan Evaluasi tidak lengkap untuk membentuk keyakinan/pendapat memadai. Indikator umum:
- Dokumen kriteria/regulasi tidak dilampirkan
- Bukti pendukung temuan tidak dilampirkan (foto, surat, transkrip rapat)
- Surat tugas/SK terkait tidak ada di folder penugasan
- Dokumen objek pengawasan tidak lengkap

## Kriteria
- Standar Audit AAIPI / Permenpan RB 19/2009 — pendokumentasian wajib semua tahap
- SOP Inspektorat II Komdigi — pendokumentasian bukti & kertas kerja
- Per jenis pengawasan: standar khusus di SKILL.md skill spesifik

## Akibat
- Tim QC SAIPI tidak bisa menelusuri keyakinan temuan
- Risiko temuan ditolak ke tahap Pengendali Mutu
- Bila penugasan eskalasi ke ranah hukum, dokumen tidak siap

## Sebab Umum
- Auditor kurang familiar dengan standar pendokumentasian
- Time pressure: dokumen di-skip
- Tidak ada checklist kelengkapan dokumen per-tahapan

## Rekomendasi Pattern
- PPK/PT memastikan checklist kelengkapan dokumen tercentang sebelum tutup
- Tim auditor pakai pre-flight check dokumen di tahap awal
- SOP pendokumentasian dievaluasi dan di-internalisasi ulang

## Catatan
Pattern starter — disusun saat skill `evaluasi-umum` belum punya pattern historis. Akan di-deprecate setelah ≥5 pattern historis dari penugasan riil terbentuk.

# Paket Usulan Penyelarasan Konsep SK "Standar Dokumen Penugasan Pengawasan" dengan Sistem Audit AI v9 (INTEGRAL)

> Dokumen kerja untuk tim penyusun SK. Prinsip: **SK diselaraskan mengikuti sistem (v9 sebagai jangkar)**, bukan sistem tunduk pada birokrasi dokumen. Ringkasan eksekutif untuk pimpinan: [`penyelarasan-juknis-v8.html`](penyelarasan-juknis-v8.html). Rencana & status implementasi: [`RENCANA-IMPLEMENTASI-v9.md`](RENCANA-IMPLEMENTASI-v9.md).

## 1. Prinsip pembatas

- **v9 = mesin produksi substansi.** Garis finis = **laporan disetujui** (sign‑off QA/QC berjenjang).
- **Setelah laporan disetujui = ranah administrasi** (Tahapan 8, peran **TU**): penyampaian, distribusi, pemantauan tindak lanjut, arsip.
- **Garis serah:** pada persetujuan, v9 mengekspor **LHP final + Daftar Temuan & Rekomendasi** ke administrasi. Penomoran resmi, TTE, distribusi, dan arsip tetap di **SIMWAS**.
- **Klausul digital‑native (usulan masuk SK):** dokumen penugasan boleh **dihasilkan sistem**; persyaratan validasi berjenjang & keterlacakan dianggap terpenuhi melalui **jejak audit sistem (audit trail)** — tidak mensyaratkan tanda tangan/paraf manual berlapis untuk tiap dokumen antara.

## 2. Pemetaan 36 Template SDP ↔ v9

Perlakuan: **ADOPSI** (diserap memperkuat produksi) · **ADA** (sudah di v9) · **FIELD** (jadi field, bukan dokumen) · **EKSPOR** (artefak garis serah) · **ADMIN** (ranah administrasi/SIMWAS, bukan diproduksi v9) · **GABUNG** (konsolidasi).

| SDP | Nama | Status Juknis | Perlakuan v9 | Keterangan |
|---|---|---|---|---|
| L.01–L.05 | LHA/LHR/LHE/Lap Pemantauan/Memo | WAJIB | **ADA** | `render_report` jenis‑aware, shell kop seragam |
| L.06 | Ringkasan Eksekutif | WAJIB | **ADA** | section laporan, frasa assurance per jenis |
| P.01 | Surat Tugas | WAJIB | **ADMIN** | dari SIMWAS (`nomor_st`) |
| P.02 | Kartu Penugasan | WAJIB | **ADA** | tab KP + template v2.0 |
| P.03 / P.04 | Alokasi Waktu / Anggaran | WAJIB | **FIELD** | jadi field di KP/PKP (hapus dok + TTD terpisah; stop anggaran 3×) |
| P.05 | Survei Pendahuluan | WAJIB | **ADA (audit‑only)** | Tahapan 0; **usul SK: wajib audit saja** |
| P.06 | PKP | WAJIB | **ADA** | tab PKP + template v2.0 (I/II/III) |
| PL.08 | KKP | WAJIB | **ADA** | temuan.json + render_kkp (KKSAR jenis‑aware) |
| PL.09 | Catatan Hasil Pengujian | WAJIB | **GABUNG→KKP** | overlap dengan KKP |
| PL.10 | Indeksasi & Tickmarks | WAJIB | **EKSPOR/auto** | kode/`no_kkp` otomatis; tickmark manual usang |
| PL.11 | Lap Monitoring & Pengendalian | WAJIB | **auto** | dari jejak `agent_runs` (audit trail) |
| PL.04 | Surat Permintaan Data | WAJIB | **ADMIN** | seremonial; data di‑upload langsung |
| PL.01/02/03/05/06/07 | Pengantar/Pakta/Notulensi/Penyerahan/Penolakan data | OPSIONAL | **ADMIN** | seremonial → opsional/kondisional |
| K.01 | Daftar Hasil Pengawasan (DHP) | WAJIB | **EKSPOR** | auto‑generate "Daftar Temuan & Rekomendasi" saat approval |
| K.02/K.06 | Surat Penyampaian / Pengantar Masalah | WAJIB/OPS | **ADMIN** | draft Surat Penyampaian di Tahapan 8 (TU) |
| K.03 | BA Pembahasan (exit meeting) | WAJIB | **ADMIN** | catatan pembahasan (administrasi) |
| K.04 | Notulensi Kesepakatan | OPSIONAL | **GABUNG→K.03** | duplikat BA Pembahasan |
| K.05 | Lembar Persetujuan DHP | WAJIB | **ADMIN** | e‑persetujuan klien 1× (bukan TTD 3×) |
| K.07 | Log Komunikasi | OPSIONAL | **auto** | dari audit trail |
| M.01/M.02/M.03 | Reviu Supervisi / Daftar Periksa QA‑QC / Sign‑off | WAJIB | **ADA+GABUNG** | **Lembar Kendali Mutu Berjenjang** (KT self → PT supervisi+verdict → PM QA/QC 14 butir) |
| TL.01–TL.03 | Pemantauan Tindak Lanjut | WAJIB | **ADMIN→TLHP** | modul TLHP (auto‑ingest saat approval); TL.02+03 dilebur jadi register |

**Ringkas:** dari 36 → inti **produksi ~14** (sudah di v9) + **~12 auto‑generate/field/ekspor** + sisanya **administrasi/SIMWAS** (opsional/kondisional). Konsolidasi: 36 → ±20 dokumen efektif.

## 3. Matriks proporsionalitas dokumen produksi WAJIB per jenis penugasan

Pengganti "27 WAJIB seragam". ✓ wajib · ○ kondisional · – tidak relevan.

| Dokumen produksi | Audit | Reviu | Evaluasi | Pemantauan | Konsultansi |
|---|:--:|:--:|:--:|:--:|:--:|
| Survei Pendahuluan | ✓ | ○ | ○ | – | – |
| Kartu Penugasan (KP) | ✓ | ✓ | ✓ | ✓ | ✓ |
| PKP | ✓ | ✓ | ✓ | ✓ | ○ |
| KKP & Temuan | ✓ | ✓ | ✓ | ✓ | ○ |
| Lembar Kendali Mutu Berjenjang | ✓ | ✓ | ✓ | ✓ | ○ |
| Laporan + Ringkasan Eksekutif | LHA | LHR | LHE | LHP | Memo |
| Daftar Temuan & Rekomendasi (ekspor) | ✓ | ✓ | ✓ | ✓ | – |

Catatan: Konsultansi advisory (tanpa temuan → saran). Unsur **Sebab** diisi untuk audit/reviu/evaluasi non‑LKE/pemantauan; **tidak** untuk evaluasi ber‑LKE (RB/SAKIP/SPIP) & konsultansi. *Sistem v9 sudah menerapkan proporsionalitas ini secara emergen: Survei hanya audit; Daftar Temuan hanya bila ada temuan; kolom/elemen KKP & paradigma laporan menyesuaikan jenis.*

## 4. Errata konsistensi Konsep SK (untuk diperbaiki di draft)

| # | Temuan inkonsistensi | Usulan perbaikan |
|---|---|---|
| 1 | Struktur laporan campur: LHA "BAB I–IV" vs LHR/LHE/Pemantauan "A/B/C" | Seragamkan **shell**: Nota Dinas → Cover → Isi (Pendahuluan → Hasil → Simpulan → Rekomendasi/Saran) |
| 2 | Istilah unsur "liar": "Analisis Penyebab", "Dampak/Risiko", "Tingkat Capaian", "Catatan" | Baku‑kan ke **KKSAR**: Kondisi · Kriteria · **Sebab** · **Akibat** · Rekomendasi (variasi per jenis = *pengurangan unsur*, bukan ganti nama) |
| 3 | Istilah jenis: **ADTT vs PDTT** dipakai bergantian | Pilih satu istilah baku, seragamkan semua template |
| 4 | Kata "audit/diaudit/Tim Audit" bocor di template lintas‑jenis | Ganti netral "pengawasan/penugasan" |
| 5 | Ringkasan Eksekutif memakai frasa "keyakinan memadai" untuk pemantauan/konsultansi (non‑assurance) | Frasa RE **per jenis** (assurance vs non‑assurance) |
| 6 | Survei Pendahuluan 100% audit‑centric tapi diwajibkan semua jenis | **Wajib audit saja**; opsional jenis lain |
| 7 | Anggaran muncul 3× (KP field, Alokasi Waktu kolom Biaya, Alokasi Anggaran) | Jadikan **field** di KP/PKP; hapus dokumen terpisah |
| 8 | Kartu Penugasan: **dua bagian berlabel "F"**; PKP: PM hilang dari identitas tapi ikut TTD | Perbaiki penomoran & identitas penandatangan |
| 9 | 3 dokumen mutu (M.01/02/03) menulis ulang reviu berjenjang yang sama | **Gabung** jadi satu Lembar Kendali Mutu Berjenjang |
| 10 | "Daftar temuan" dilahirkan ulang di 5 template (K.01/02/05/06 + lampiran); klien TTD 3× | **Satu** Daftar Temuan & Rekomendasi dirujuk; persetujuan klien 1× |
| 11 | PL.04 Permintaan Data WAJIB tapi PL.05 Penyerahan Data OPSIONAL (asimetris); PL.06+PL.07 duplikat | Gabung jadi BA Serah‑Terima Data; penolakan cukup satu dokumen |
| 12 | TL.02 (per‑temuan, klien) ≈ TL.03 (rekap, APIP) | Lebur jadi satu register tindak lanjut |
| 13 | Penomoran surat hardcode `PW.01.06` / typo ("sampa", "1J") di sebagian template | Klasifikasi nomor per jenis; rapikan typo & Petunjuk Pengisian sisa template "Kegiatan/Lapgas" |

## 5. Bukti kesiapan sistem (status implementasi v9)

| Fase | Hasil |
|---|---|
| 0 | Peran **TU**; password seed via env (repo publik aman); DB terisolasi |
| 1 | Format laporan KKSAR terpadu (istilah baku dikunci di PANDUAN) |
| 1A | Agen AT pakai **Root Cause Analysis** (5 Whys + Fishbone) untuk Sebab |
| 1B | Agen KT bisa sisip **tabel & diagram** ke laporan |
| 2 | **Lembar Kendali Mutu Berjenjang** (KT → PT → PM QA/QC 14 butir) |
| 3 | Auto‑generate **Daftar Temuan & Rekomendasi** di garis serah |
| 4 | **Tahapan 8 Administrasi (TU)** — paket ekspor + draft Surat Penyampaian |

## 6. Rekomendasi tindak lanjut

1. Bawa **errata (§4)** ke rapat revisi draft Konsep SK.
2. Sahkan **matriks proporsionalitas (§3)** & **pemetaan SDP↔v9 (§2)** sebagai lampiran SK.
3. Masukkan **klausul digital‑native (§1)** agar dokumen produksi sah dihasilkan sistem.
4. Tetapkan batas tegas **produksi (v9) vs administrasi (SIMWAS)** di batang tubuh SK.

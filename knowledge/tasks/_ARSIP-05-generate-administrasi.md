# [ARSIP] Task 05 — Generate Administrasi (Nota Dinas + Penomoran + TTD)

> ⚠️ **STATUS: DIARSIPKAN per 16 April 2026 (v2.7)**
> Tahap administrasi (pembuatan Nota Dinas, pengisian nomor surat, tanggal, TTD) **tidak lagi dijalankan oleh Claude**. Auditor mengerjakan administrasi secara **manual** di atas output Task 04 (LHP Substansi) — mengisi nomor surat dari SIMWAS, tanggal, destinatari, tembusan, dan menandatangani langsung di Word.
>
> **Alasan**: (1) nomor surat selalu harus diambil manual dari SIMWAS (tidak bisa diotomasi), (2) TTD wajib dilakukan manusia, (3) menghemat token + waktu eksekusi, (4) Nota Dinas pengantar adalah template singkat yang lebih cepat ditulis auditor langsung.
>
> File ini disimpan sebagai **referensi historis** — isinya tidak dipakai di alur v2.7.

---

> **Model**: `claude-haiku-4-5-20251001` — Pengisian form administratif, penomoran surat, template Nota Dinas standar.

## Tujuan
Melengkapi elemen **administratif dan formal** laporan setelah substansi disetujui auditor. Tahap ini menghasilkan dokumen yang siap ditandatangani dan dikirim ke auditan.

---

## Prasyarat
⚠️ STOP jika belum ada konfirmasi auditor bahwa substansi LHP (Task 04) sudah disetujui.
Koreksi substansi (temuan, analisis, rekomendasi) **harus diselesaikan di Task 04**, bukan di sini.

---

## Informasi yang Dibutuhkan dari Auditor

**PRINSIP**: Task 05 tidak perlu menunggu semua informasi lengkap. Jalankan dengan placeholder untuk field yang belum diisi, auditor melengkapi manual sebelum TTD.

| Informasi | Sumber | Jika Tidak Ada |
|-----------|--------|----------------|
| Nomor LHP | Tanyakan ke auditor — format: `B-[XX]/IJ.3/[kode]/[bulan]/[tahun]` | Gunakan `[NOMOR-LHP]/IJ.3/PW.04.04/[BULAN]/[TAHUN]` |
| Tanggal LHP | Tanyakan ke auditor | Gunakan `[TANGGAL LHP]` — jangan crash |
| Nama & NIP Inspektur | Tanyakan ke auditor | Gunakan `[Nama Inspektur II]` + `[NIP Inspektur II]` |
| Destinatari (Kepada Yth.) | Dari context.md (`Penerima Laporan`) | Gunakan `[Destinatari]` |
| Tembusan | Tanyakan jika tidak di context.md | Gunakan `[Tembusan]` |
| Nomor ND Permintaan | Dari context.md (kosong jika PKPT) | Skip paragraf jika kosong |
| Link Survei SIMWAS | Dari context.md (kosong jika `—`) | **Skip paragraf survei jika kosong** |

**JANGAN crash atau berhenti** hanya karena field kosong/belum diisi. Masukkan placeholder dan lanjutkan.

> **Catatan template**: Template LHP lama mungkin berisi konten dari penugasan sebelumnya di bagian Nota Dinas (nama paket lama, nomor lama). Saat mengisi, **update seluruh teks Nota Dinas** dengan obyek pengadaan yang baru — jangan hanya mengganti placeholder.

---

## Langkah Eksekusi

### 1. Muat konteks
Baca `context.md` dan `_LHP/LHP-SUBSTANSI-[nomor-ST].docx`.

Update context.md:
```
Status : TAHAP 3 — ADMINISTRASI
```

### 2. Susun Nota Dinas Pengantar

Buat file Word terpisah: `_LHP/01-Nota-Dinas-[nomor-ST].docx`

Format:
```
[KOP SURAT]
Kementerian Komunikasi dan Digital RI
Inspektorat Jenderal — Inspektorat II
Jl. Medan Merdeka Barat No. 9, Jakarta 10110

────────────────────────────────────────

NOTA DINAS
Nomor: [Nomor ND]

Kepada Yth. : [Jabatan penerima dari context.md]
Dari        : Inspektur II
Hal         : Laporan Hasil [Jenis] [Obyek] [Periode/Tahun]
Klasifikasi : Biasa
Lampiran    : Satu laporan
Tanggal     : [Tanggal LHP]

Menindaklanjuti [Surat Tugas / Nota Dinas Permintaan Nomor ... tanggal ...],
kami telah melaksanakan [jenis pengawasan] terhadap [obyek]. Bersama ini kami
sampaikan laporan hasil [jenis] sebagaimana terlampir pada Nota Dinas ini.

[JIKA ada Link Survei SIMWAS — tambahkan paragraf:]
Kami mohon kesediaan Saudara/i untuk mengisi survei kepuasan atas hasil
[jenis] melalui tautan berikut: [Link SIMWAS] (minimal lima pegawai).

Terima kasih telah membantu kami dalam menjaga integritas. Demikian Nota
Dinas ini kami sampaikan. Atas perhatian dan kerja sama Bapak/Ibu kami
ucapkan terima kasih.

                                        Jakarta, [Tanggal LHP]
                                        Inspektur II,


                                        [Nama Inspektur II]
                                        NIP: [NIP Inspektur II]

Tembusan:
[Daftar tembusan — biasanya: Inspektur Jenderal Kementerian Komunikasi dan Digital RI]
```

### 3. Lengkapi LHP dengan elemen formal

Buka `_LHP/LHP-SUBSTANSI-[nomor-ST].docx` dan tambahkan/isi:

#### Elemen yang dilengkapi:
- **Nomor LHP** di header/bagian atas laporan
- **Tanggal LHP**
- **Destinatari** (Kepada Yth. + jabatan + unit + "di Jakarta")
- **Tembusan** (jika ada)
- **Blok tanda tangan** di bagian penutup:
  ```
                    Jakarta, [Tanggal]
                    [Jabatan Inspektur],


                    [Nama Inspektur II]
                    NIP: [NIP]
  ```

#### Elemen yang tetap sebagai placeholder (diisi manual sebelum TTD):
- Tanda tangan basah/elektronik — tidak bisa diisi oleh Claude
- Jika nomor surat belum diberikan: biarkan `[Nomor LHP]`

Simpan sebagai: `_LHP/02-LHP-[nomor-ST].docx`

### 4. Periksa konsistensi

Sebelum menyerahkan ke auditor untuk finalisasi, periksa:
- [ ] Nomor surat konsisten antara Nota Dinas dan LHP
- [ ] Tanggal konsisten di semua bagian
- [ ] Nama obyek konsisten (tidak ada singkatan yang berbeda)
- [ ] Nomor catatan/temuan konsisten antara ringkasan dan uraian
- [ ] Tabel rekomendasi mencantumkan semua rekomendasi dari bagian C
- [ ] Paragraf simpulan mencerminkan jumlah catatan yang ada
- [ ] Jika ada survei SIMWAS: link tercantum di Nota Dinas

### 5. Update context.md
```
Status          : SELESAI — MENUNGGU TTD AUDITOR
Tanggal LHP     : [tanggal]
Nomor LHP       : [nomor]
File Nota Dinas : _LHP/01-Nota-Dinas-[nomor-ST].docx
File LHP Final  : _LHP/02-LHP-[nomor-ST].docx
```

### 6. Konfirmasi kepada auditor

```
=== DOKUMEN SIAP TTD ===
File yang dibuat:
  1. _LHP/01-Nota-Dinas-[nomor-ST].docx  ← Nota Dinas pengantar
  2. _LHP/02-LHP-[nomor-ST].docx         ← Laporan Hasil Pengawasan

Checklist sebelum TTD:
  ✅ Substansi (temuan, analisis, rekomendasi) — sudah disetujui di Task 04
  [  ] Nomor surat — [sudah terisi / masih placeholder, mohon diisi]
  [  ] Tanggal     — [sudah terisi / masih placeholder, mohon diisi]
  [  ] Nama & NIP Inspektur — [sudah terisi / masih placeholder]
  [  ] Tanda tangan — diisi auditor

⚠️ Jika ada koreksi SUBSTANSI (temuan/analisis/rekomendasi):
   → Kembali ke Task 04 (bukan diubah di sini)
⚠️ Jika ada koreksi ADMINISTRATIF (nomor, tanggal, nama):
   → Bisa langsung diedit di file Word oleh auditor
```

---

## Output
- `_LHP/01-Nota-Dinas-[nomor-ST].docx`
- `_LHP/02-LHP-[nomor-ST].docx`
- `context.md` dengan status SELESAI

---

## Pemisahan Tanggung Jawab

```
Substansi (Temuan/Analisis/Rekomendasi) → Task 04 ← diiterasi bersama auditor
Administrasi (Nomor/Tanggal/TTD)        → Task 05 ← diselesaikan sekali di akhir
```

Prinsip ini memastikan diskusi substansi tidak terganggu oleh urusan penomoran surat, dan dokumen final tidak perlu dibuat ulang hanya karena perubahan substansi minor.

---

## Catatan
- Nomor surat dan tanda tangan **wajib diisi/disetujui manusia** — Claude hanya menyiapkan struktur
- Jika setelah Task 05 ada temuan baru atau koreksi substansi: buat versi baru (`-v2.docx`) via Task 04, lalu ulang Task 05
- Kode nomor surat sesuai jenis: Audit/Reviu = `PW.04.04`, Evaluasi = `PW.04.05`, Pemantauan = `PW.04.06`

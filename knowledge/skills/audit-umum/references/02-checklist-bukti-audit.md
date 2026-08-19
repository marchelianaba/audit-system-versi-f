# Checklist Bukti Audit — Skill audit-umum

## Prinsip Kecukupan Bukti (SAIPI)

Bukti audit yang **memadai** untuk mendukung temuan harus memenuhi:

- **Cukup (sufficient)** — kuantitas memadai untuk membentuk simpulan
- **Kompeten (competent)** — relevan, andal, valid
- **Relevan** — berhubungan langsung dengan kriteria/tujuan audit

## Hierarki Sumber Bukti (urut dari paling kuat)

1. **Bukti fisik** — observasi langsung, foto bertanggal, GPS, BAST
2. **Bukti dokumenter primer** — kontrak asli ber-TTD, SP2D, BA Resmi, kuitansi asli
3. **Bukti dokumenter sekunder** — copy, scan, laporan internal, notulen
4. **Bukti analitis** — perhitungan, rekonsiliasi, perbandingan benchmark
5. **Bukti konfirmasi** — surat konfirmasi dari pihak ketiga
6. **Bukti testimoni** — wawancara, BA klarifikasi (paling lemah; harus tertulis)

## Aturan Kecukupan per Level Materialitas

| Level temuan | Minimal jenis bukti | Catatan |
|--------------|---------------------|---------|
| Catatan administratif | 1 dokumenter sekunder | Boleh testimoni saja jika fakta non-finansial |
| Reguler | 2 dari hierarki, salah satu primer | Cross-check antar dokumen |
| Material | 3 dari hierarki, **wajib ada primer** | Konfirmasi tertulis pihak terkait |
| Prioritas tinggi | 4+ dari hierarki + perhitungan kerugian | Eskalasi & verifikasi independen |

## Format Pencatatan Bukti

Setiap bukti dicatat di KKA Sheet "Daftar Bukti" dengan kolom:

```
ID    | Nama File                | Halaman | Tipe        | Tanggal Dok | Ringkasan Isi    | Hash/Versi
B-001 | Kontrak-PSrE-2026.pdf    | 5       | primer-doc  | 2026-02-14  | Pasal nilai      | sha256:abcd…
```

Setiap temuan di KKA harus mereferensikan **minimal** jumlah bukti sesuai level materialitasnya, dengan format `[B-001 hal. 5 par. 3]`.

## Pengujian Kualitas Bukti

Sebelum bukti dipakai sebagai pendukung temuan, lakukan:

- [ ] **Otentikasi** — TTD asli? cap basah? digital signature valid?
- [ ] **Ketepatan tanggal** — apakah tanggal dokumen konsisten dengan kronologi?
- [ ] **Ketepatan angka** — penjumlahan, perkalian, sub-total benar?
- [ ] **Konsistensi antar dokumen** — nilai/lingkup/pihak sama di seluruh dokumen terkait?
- [ ] **Kesesuaian dengan regulasi formil** — format wajib menurut juklak (mis. KAK harus ada nomor & TTD KPA)

## Red Flag Bukti

Catat dan eskalasi jika ditemukan:

- Tanggal dokumen mendahului dokumen yang seharusnya menjadi prasyaratnya
- Tanda tangan tidak konsisten antar dokumen dari orang yang sama
- Salinan tanpa cap "sesuai aslinya"
- Dokumen dengan stempel/format tidak sesuai
- Selisih angka yang tidak dapat dijelaskan antar dokumen
- Dokumen yang seharusnya wajib ada tetapi "tidak ditemukan"

## Keterbatasan Bukti — Cara Mencatat

Jika bukti yang seharusnya ada tidak diperoleh:

1. Catat di KKA Sheet "Audit Trail" dengan timestamp permintaan ke auditan
2. Berikan tenggat klarifikasi (default 3 hari kerja)
3. Jika setelah tenggat tetap tidak ada bukti:
   - Untuk temuan **non-material**: catat sebagai keterbatasan, lanjutkan
   - Untuk temuan **material**: catat sebagai **scope limitation** di Bab Metodologi LHA dan turunkan tingkat keyakinan untuk aspek tersebut
   - Untuk temuan **prioritas tinggi**: stop dan eskalasi ke Inspektur sebelum lanjut

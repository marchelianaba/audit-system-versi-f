# [ARSIP] Task Legacy — Reviu Temuan Interaktif

> **STATUS: DIARSIPKAN (tidak lagi bagian dari alur v2.7+).**
>
> File ini dipertahankan hanya sebagai referensi historis. Alur reviu temuan sekarang terintegrasi di Task 03 (persetujuan KKP per-gate) dan Task 04 (persetujuan LHP). Jangan mengeksekusi task ini untuk penugasan baru.
>
> **Catatan penomoran**: Nomor "Task 05" pada header lama di file ini TIDAK terkait dengan `_ARSIP-05-generate-administrasi.md` (Task 05 Administrasi yang juga sudah diarsipkan). Keduanya independen dan sama-sama tidak aktif.
>
> **Model (historis)**: `claude-sonnet-4-6` — Dialog iteratif review temuan, memerlukan pemahaman konteks audit mendalam.

## Tujuan
Task interaktif untuk membantu auditor mereviu setiap temuan satu per satu, mengkonfirmasi, memodifikasi, atau menghapus temuan dari draft KKP.

## Langkah Eksekusi

1. **Baca `_KKP/temuan-draft.json`** dan hitung total temuan.

2. **Tampilkan ringkasan awal:**
   ```
   === REVIU TEMUAN INTERAKTIF ===
   Total temuan dalam draft: [X]
   Temuan material (> Rp 500 juta): [Y]
   Temuan sedang (Rp 100-500 juta): [Z]
   Temuan minor (< Rp 100 juta): [W]

   Ketik MULAI untuk memulai reviu satu per satu.
   ```

3. **Untuk setiap temuan**, tampilkan:
   ```
   === TEMUAN [N] dari [X] ===
   Judul: [xxx]
   Area: [xxx]
   Level Keyakinan: [Tinggi/Sedang/Rendah]
   Estimasi Nilai: Rp [xxx]

   KONDISI: [teks kondisi]
   KRITERIA: [pasal peraturan]
   SEBAB: [analisis sebab]
   AKIBAT: [dampak]
   REKOMENDASI: [saran tindak]

   Dokumen Sumber: [nama file, halaman]

   Pilihan:
   [S] Setujui → masuk KKP final
   [E] Edit → masukkan revisi
   [H] Hapus → tidak masuk KKP
   [T] Tunda → reviu nanti
   [?] Tampilkan dokumen sumber
   ```

4. **Proses input auditor:**
   - `S` → tandai temuan sebagai APPROVED, lanjut ke temuan berikutnya
   - `E` → minta teks revisi dari auditor, update temuan, tandai EDITED
   - `H` → konfirmasi "Yakin hapus temuan ini? (Y/N)", tandai DELETED
   - `T` → lewati, masuk daftar "Ditunda"
   - `?` → tampilkan nama file dan lokasi dokumen sumber

5. **Setelah semua temuan direviu**, tampilkan ringkasan:
   ```
   === HASIL REVIU ===
   Disetujui: [X] temuan
   Diedit: [Y] temuan
   Dihapus: [Z] temuan
   Ditunda: [W] temuan

   Ketik SIMPAN untuk generate KKP Final, atau LANJUT untuk reviu temuan yang ditunda.
   ```

6. **Jika SIMPAN**, update `temuan-draft.json` dengan status masing-masing temuan, lalu panggil Task 03 untuk generate KKP Final.

## Output
- `_KKP/temuan-draft.json` diperbarui dengan status reviu setiap temuan
- Siap untuk Task 03 (generate KKP Final)

## Catatan
- Task ini bisa dijalankan berulang kali sampai auditor puas dengan seluruh temuan
- Gunakan task ini sebelum generate KKP FINAL untuk memastikan semua temuan sudah tervalidasi

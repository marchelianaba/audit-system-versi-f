# Task 06: Rekapitulasi Bulanan

> **Model**: `claude-sonnet-4-6` — Agregasi data lintas penugasan, statistik, pembuatan laporan rekapitulasi.

## Tujuan
Scheduled task yang dijalankan setiap bulan untuk membuat rekapitulasi seluruh penugasan yang selesai, statistik temuan, dan laporan monitoring tindak lanjut.

## Jadwal Eksekusi
Direkomendasikan: Setiap tanggal 1 bulan berjalan, atau akhir bulan sebelumnya.

## Langkah Eksekusi

1. **Scan folder `penugasan/`** dan identifikasi semua sub-folder penugasan.

2. **Baca `context.md`** setiap penugasan dan kategorikan:
   - Status SELESAI (ada LHP Final)
   - Status IN PROGRESS (masih berjalan)
   - Status DRAFT (KKP belum final)

3. **Untuk penugasan SELESAI**, baca file LHP di `_LHP/` dan ekstrak:
   - Nomor ST dan obyek
   - Jenis pengawasan
   - Jumlah temuan
   - Total nilai temuan (Rp)
   - Bulan selesai

4. **Hitung statistik bulan ini:**
   - Total penugasan selesai bulan ini
   - Total penugasan berjalan
   - Total temuan yang diterbitkan
   - Total nilai temuan (Rp)
   - Breakdown per jenis pengawasan
   - Breakdown per area temuan

5. **Buat file rekapitulasi:**
   Simpan ke `laporan-bulanan/REKAP-[TAHUN]-[BULAN].xlsx` dengan sheet:
   - Sheet 1: Ringkasan Eksekutif
   - Sheet 2: Daftar Penugasan & Status
   - Sheet 3: Statistik Temuan per Area
   - Sheet 4: Penugasan In Progress

6. **Tampilkan ringkasan** di terminal:
   ```
   === REKAPITULASI [BULAN] [TAHUN] ===
   Penugasan selesai bulan ini: [X]
   Total penugasan berjalan: [Y]
   Total temuan diterbitkan: [Z]
   Total nilai temuan: Rp [xxx]
   File rekap disimpan di: laporan-bulanan/REKAP-[TAHUN]-[BULAN].xlsx
   ```

## Output
- `laporan-bulanan/REKAP-[TAHUN]-[BULAN].xlsx`
- Ringkasan di terminal

## Catatan
- Task ini aman dijalankan berulang kali (idempotent) — akan overwrite file rekap bulan yang sama
- Jika folder `laporan-bulanan/` belum ada, buat otomatis
- Untuk tindak lanjut rekomendasi, diperlukan input manual dari auditor (sistem ini tidak track tindak lanjut secara otomatis)

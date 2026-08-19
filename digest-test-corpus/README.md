# Korpus Ujicoba Digestion

Tempat menaruh dokumen untuk menguji pipeline **digestion** (TOR/RAB/KAK/HPS/RFI/KONTRAK → JSON).

## Cara pakai
1. **Taruh PDF** di subfolder sesuai jenisnya:
   ```
   digest-test-corpus/
   ├── tor/        ← TOR / KAK perencanaan (digest_tor, per-file)
   ├── rab/        ← RAB (digest_rab, per-file)
   ├── kak/        ← KAK pengadaan ┐
   ├── hps/        ← HPS           │ digest_pengadaan (folder-level,
   ├── rfi/        ← RFI vendor    │ KAK+HPS+RFI+Kontrak digabung)
   └── kontrak/    ← Kontrak       ┘
   ```
   (Boleh juga flat di root korpus bila nama file diawali `TOR-/RAB-/KAK-/HPS-/RFI-/KONTRAK-`.)
2. **Jalankan**: `./digest-test-corpus/run.sh`  (atau lihat `backend/scripts/README.md`).
3. Baca ringkasan konsol + `_digest-test/report.md`. Fokus ke bagian **"PERLU PERHATIAN"**:
   gagal / kosong / field kunci hilang / **data mungkin di gambar** / golden meleset.

## Dokumen tanpa parser & dokumen bergambar (skema dua-tingkat)
Asumsi: **tidak ada dokumen hasil scan** (dikondisikan di input), jadi teks selalu
bisa dibaca. Penanganan dua kondisi:

- **Ada parser** → digest deterministik V6 (jalur utama: gratis, cepat, reproducible).
- **Tidak ada parser / field kunci hilang** → jalankan dengan **`--llm-fallback`**:
  field yang hilang dipulihkan oleh model murah (Haiku) dari TEKS dokumen.
  ```
  ./digest-test-corpus/run.sh --llm-fallback
  ```
  Kolom **"LLM pulih"** di report menunjukkan field apa yang berhasil dipulihkan.
  Butuh `ANTHROPIC_API_KEY` (sudah ada di `.env`). Default off agar run deterministik
  tetap gratis & cepat.
- **Dokumen memuat gambar** → harness menghitung gambar tertanam (kolom **"gbr"**).
  Bila field kunci tetap hilang **dan** dokumen punya gambar, ditandai
  **"data mungkin di GAMBAR"** (datanya kemungkinan ada di tabel/diagram yang
  di-render jadi gambar — tak terbaca teks). Solusi: minta data kunci dalam bentuk
  teks/tabel, atau periksa manual.

## golden.json (opsional — ukur akurasi)
Anotasi nilai-harapan untuk **sebagian** dokumen → harness menilai akurasi ekstraksi
(substring, case-insensitive, dicocokkan ke JSON digest). Edit `golden.json` di folder ini.
Template lengkap: `backend/scripts/golden.example.json`.

## Catatan
- Dokumen di folder ini **tidak di-commit** (lihat `.gitignore`) — aman untuk dokumen
  internal/rahasia. Hanya struktur folder + README + golden.json yang ter-track.
- Output `_digest-test/` juga tidak di-commit.

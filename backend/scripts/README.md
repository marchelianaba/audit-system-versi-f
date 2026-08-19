# backend/scripts — alat dev/ujicoba

## digestion_harness.py — ujicoba pipeline digestion (banyak dokumen)

Menjalankan digest V6 yang sama dengan produksi (`digest_tor`/`digest_rab` per-file,
`digest_pengadaan` folder-level) atas sebuah korpus, **paralel**, lalu mengukur
**kecepatan + kualitas** otomatis — tanpa membaca tiap JSON manual.

### Cara pakai
```bash
# dari root repo
PATH="$PWD/backend/.venv/bin:$PATH" PYTHONPATH="$PWD/backend" \
  backend/.venv/bin/python backend/scripts/digestion_harness.py \
    --corpus /path/ke/korpus [--out folder-output] [--workers 4] [--golden golden.json] \
    [--llm-fallback] [--llm-model claude-haiku-4-5-20251001]
```
`PATH` harus memuat venv (subprocess digest pakai `python3` + butuh deps V6).

### Susun korpus (klasifikasi jenis)
Pilih salah satu — keduanya didukung:
- **Subfolder per jenis** (disarankan untuk korpus besar):
  ```
  korpus/
  ├── tor/   *.pdf
  ├── rab/   *.pdf
  ├── kak/   *.pdf
  ├── hps/   *.pdf
  ├── rfi/   *.pdf
  └── kontrak/ *.pdf
  ```
- **Prefiks nama file** (flat): `TOR-...pdf`, `RAB-...pdf`, `KAK-...pdf`, dst.

`ST/KP/PKP/OTHER` otomatis dilewati (tak punya digest script).

### Output & metrik
- Ringkasan konsol per jenis: jumlah, ok, kosong, waktu rata-rata, **% cakupan field kunci**,
  **gbr** (gambar tertanam), dan **+LLM** (field dipulihkan fallback, bila aktif).
- **Perlu perhatian**: file gagal / kosong / field hilang / **data mungkin di gambar** / golden meleset.
- `report.md` + `report.json` di folder output (default `<korpus>/_digest-test/`).

### Skema dua-tingkat untuk dokumen "tanpa parser" + bergambar
Asumsi operasional: **tidak ada dokumen scan** (teks selalu terbaca). Maka:
1. **Ada parser** → digest deterministik V6 = jalur utama (gratis, cepat, reproducible).
2. **Tidak ada parser / field hilang** → `--llm-fallback`: model murah (Haiku) membaca
   **TEKS** dokumen dan mengisi field kunci yang hilang. Hanya dipanggil untuk dokumen
   yang field-nya hilang (selektif → hemat token). Butuh `ANTHROPIC_API_KEY`
   (di `.env`; bisa override model via `--llm-model` atau env `ANTHROPIC_FALLBACK_MODEL`).
3. **Data di dalam gambar** → fallback LLM teks tak bisa menolong (datanya bukan teks).
   Harness menandai dokumen ber-gambar yang field-nya tetap hilang sebagai
   **"data mungkin di GAMBAR"** untuk ditindaklanjuti (minta data bentuk teks / cek manual).

Logika di `app/llm_extract.py` (reusable, tanpa menyentuh V6) — siap dipakai ulang
jalur produksi `_run_ingestion` bila nanti diaktifkan.

### Golden (akurasi, opsional)
Anotasi nilai-harapan untuk sebagian dokumen → skor akurasi (substring,
case-insensitive, dicocokkan ke isi JSON digest). Lihat `golden.example.json`.

```json
{
  "KAK-Data-Center-DRC-2026.pdf": { "nilai_hps": "8200000000", "obyek": "Data Center" }
}
```

> Catatan: cache lintas-penugasan (`DocumentCache`, dedup sha256) adalah fitur
> jalur APP (upload→auto-digest); harness ini selalu mengukur digest **dingin**
> (murni waktu script), supaya konsisten antar-run.

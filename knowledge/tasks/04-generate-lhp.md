# Task 04 — Generate LHP Substansi (Tahap Akhir Otomasi) — v4

> **Model**: `claude-sonnet-4-6` — Narasi analitik, menulis temuan lengkap, rekomendasi, simpulan berkualitas tinggi.

> **Hanya boleh dijalankan oleh role: Ketua Tim (KT), Pengendali Teknis (PT), atau Pengendali Mutu (PM)**. Akan ditolak oleh `scripts/role_check.py` jika anggota tim mencoba menjalankannya.

## Tujuan
Mengisi bagian **substantif** laporan hasil pengawasan dari template. Konsumsi `_KKP/temuan.json` (yang sudah disusun anggota-anggota tim) sebagai sumber data temuan, agregasikan, lalu tulis LHP.

**Task 04 adalah tahap akhir yang dikerjakan Claude.** Setelah LHP Substansi disetujui, auditor melanjutkan **secara manual**: mengisi nomor surat (dari SIMWAS), tanggal, destinatari, tembusan, membuat Nota Dinas pengantar, dan menandatangani.

---

## Pre-Check v4 (WAJIB sebelum mulai)

```bash
# 1. Role check — tolak kalau bukan Ketua Tim / PT / PM
python3 scripts/role_check.py --penugasan penugasan/[nama] --task 04

# 2. Completeness check — semua sasaran HARUS sudah SELESAI_KKP
python3 scripts/sasaran_completeness.py --penugasan penugasan/[nama] --emit-reminder
# Exit 0 = boleh lanjut.
# Exit 2 = ada sasaran belum dikerjakan → SCRIPT mencetak reminder ke ketua tim
#          (siapa yang belum, sasaran mana). LHP DIBLOKIR. Jangan lanjut.
```

Jika completeness check gagal:
1. Salin output reminder ke chat (untuk visibility ketua tim).
2. Jelaskan ke ketua tim: hubungi anggota yang belum kerjakan KKP.
3. STOP. Jangan teruskan ke langkah lain.

```bash
# 3. Validasi temuan.json (sumber data utama LHP)
python3 scripts/validate_kkp_json.py penugasan/[nama]/_KKP/temuan.json

# 4. Log start
python3 scripts/audit_trail.py log-event --penugasan penugasan/[nama] \
  --action TASK_STARTED --task 04 --target _LHP/LHP-SUBSTANSI.docx
```

---

## Prasyarat
⚠️ STOP jika belum ada konfirmasi auditor (anggota tim) atas KKP-nya masing-masing via chat.
Task ini hanya dijalankan setelah:
- Semua sasaran di `sasaran-assignment.json` berstatus `SELESAI_KKP` atau lebih
- `_KKP/temuan.json` valid terhadap schema

---

## Pembagian Tanggung Jawab — Claude vs Auditor Manual

| Aspek | Task 04 (Claude) | Setelah Task 04 (Auditor Manual) |
|-------|------------------|-----------------------------------|
| Fokus | Konten: temuan, analisis, rekomendasi | Form: nomor surat, tanggal, Nota Dinas, TTD |
| Dapat diiterasi? | **Ya — sebanyak yang diperlukan** | Sekali, di Word langsung |
| Yang diisi | Semua bagian substantif | Semua elemen formal |
| Yang dikosongkan (sebagai placeholder `[DIISI AUDITOR]`) | Nomor surat, tanggal, destinatari, tembusan, TTD | — |
| Nota Dinas pengantar | **Tidak dibuat** — auditor menulis sendiri di Word (format singkat, lihat Catatan di bawah) | Ditulis + ditandatangani |

---

## Langkah Eksekusi

### 1. Muat konteks
Baca `context.md`. Update:
```
Status : TAHAP 2 — LHP SUBSTANSI
```

### 2. Render LHP (v4.0.4 — placeholder-driven)

**Strategi v4.0.4**: gunakan `scripts/render_lhp.py` yang find-replace placeholder `{{...}}` di template `templates/_skeleton-lhp/template-lhp-[jenis].docx`. Ini memotong waktu Task 04 dari ~tulis 180-paragraf-from-scratch jadi just isi argumen + jalan.

```bash
# 1. Tulis rekomendasi.json — mapping per id_temuan ke teks rekomendasi
cat > "penugasan/[nama]/_LHP/rekomendasi.json" << 'EOF'
{
  "T-001": "Memperbaiki ... [rekomendasi spesifik untuk T-001]",
  "T-002": "Memutakhirkan ... [rekomendasi spesifik untuk T-002]"
}
EOF

# 2. Render LHP
python3 scripts/render_lhp.py \
  --penugasan "penugasan/[nama]" \
  --rekomendasi-file "penugasan/[nama]/_LHP/rekomendasi.json" \
  --judul "Pengadaan ... Tahun 2026" \
  --auditi "Direktorat XYZ" \
  --dasar-permintaan "Nota Dinas Direktur ... perihal Permohonan Reviu ..." \
  --gambaran-umum "Pengadaan ini adalah ...  (3-5 kalimat narasi)" \
  --tanggal-exit-meeting "12 Mei 2026"
```

Output: `_LHP/LHP-SUBSTANSI-[slug-nomor-st].docx` dengan struktur lengkap (Nota Dinas placeholder + halaman judul + A. Dasar Pelaksanaan ... I. Apresiasi). Section H. Tanggapan Auditi otomatis ditulis sebagai placeholder `[DIISI AUDITI ...]`.

Claude **tidak perlu** menulis script python-docx custom untuk LHP — pakai renderer. Kalau ada section khusus skill yang renderer belum support, edit skeleton template (`templates/_skeleton-lhp/template-lhp-[jenis].docx`) dengan placeholder baru, bukan generate dari scratch.

**Fallback** (kalau renderer fail): duplikat skeleton template lalu edit manual.
```bash
cp "templates/_skeleton-lhp/template-lhp-[jenis].docx" "_LHP/LHP-SUBSTANSI-[nomor-ST].docx"
```

### 2b. Konsumsi `_KKP/temuan.json` (v4)

LHP **wajib** dibangun dari `temuan.json`, bukan dari Word KKP. Iterasi setiap entry:

```python
# pseudocode:
import json
with open("penugasan/[nama]/_KKP/temuan.json") as f:
    kkp = json.load(f)

# Group temuan per sasaran untuk struktur LHP
per_sasaran = {}
for t in kkp["temuan"]:
    per_sasaran.setdefault(t["sasaran_id"], []).append(t)

# Tiap section "Hasil Pengawasan" berisi temuan dari semua anggota
# yang mengerjakan sasaran tsb (bisa dari beberapa anggota berbeda).
```

Catatan ketua tim (jika ada koreksi substantif untuk temuan tertentu) dapat di-set di field `catatan_ketua_tim` di `temuan.json` sebelum LHP final.

### 3. Isi bagian substantif

Bagian yang **DIISI** di Task 04:

#### A. Pendahuluan
- Latar Belakang: konteks penugasan, dasar hukum fungsi pengawasan
- Dasar Pelaksanaan: nomor ST (dari context.md)
- Tujuan dan Sasaran: sesuai scope yang tercantum di KKP
- Ruang Lingkup: dokumen/aspek yang diperiksa, yang tidak dicakup
- Metodologi: cara kerja (desk review, wawancara, dll)
- Jangka Waktu: dari context.md
- Komposisi Tim: dari context.md

#### B. Gambaran Umum Obyek Pengawasan
- Profil singkat obyek: unit/paket/instansi yang diawasi
- Data relevan: nilai kontrak/anggaran, periode, PPK/pejabat terkait

#### C. Hasil Pengawasan
Uraian per catatan dari KKP yang sudah dikonfirmasi.

Untuk setiap catatan, gunakan format:

```
[NOMOR] [JUDUL TEMUAN]

Kondisi    : [uraikan fakta — lebih naratif dari KKP, dengan konteks yang cukup]

Kriteria   : [teks normatif pasal/ketentuan yang menjadi acuan]

Akibat     : [konsekuensi/risiko dari kondisi yang ditemukan;
              jika kondisi sudah sesuai: "Tidak ditemukan dampak negatif dari aspek ini."]

Rekomendasi: [tindakan perbaikan spesifik: apa, siapa, kapan]
              [kosong jika kondisi sudah sesuai]
```

Catatan yang sudah sesuai ketentuan: tulis uraian singkat bahwa aspek tersebut terpenuhi. Tidak perlu rekomendasi.

#### D. Simpulan
Paragraf simpulan dengan bahasa keyakinan sesuai jenis pengawasan:

- **Audit (keyakinan memadai):**
  > "Berdasarkan prosedur audit yang telah kami lakukan, menurut pendapat kami [obyek] telah/belum mematuhi ketentuan yang berlaku dalam hal [aspek], kecuali hal-hal yang kami ungkapkan pada bagian hasil pengawasan."

- **Reviu (keyakinan terbatas):**
  > "Berdasarkan hasil reviu secara terbatas, tidak terdapat hal-hal yang membuat kami yakin bahwa [aspek] tidak terpenuhi sesuai ketentuan, kecuali hal-hal yang kami sampaikan pada bagian hasil reviu di atas."

- **Pemantauan:**
  > "Berdasarkan hasil pemantauan per [tanggal], progres pelaksanaan pekerjaan [sesuai/tidak sesuai] dengan jadwal kontrak. Terdapat [N] isu yang memerlukan perhatian sebagaimana diuraikan pada bagian hasil pemantauan."

- **Evaluasi:**
  > "Berdasarkan hasil evaluasi, [aspek yang dievaluasi] telah/belum memenuhi kriteria yang ditetapkan, dengan [N] catatan yang perlu ditindaklanjuti."

#### E. Rekomendasi
Tabel kompilasi rekomendasi dari bagian C:

| No | Rekomendasi | Penanggung Jawab | Tenggat |
|----|-------------|-----------------|---------|
| 1  | [teks]      | [jabatan]       | [tenggat] |

Hanya catatan yang memerlukan tindakan yang masuk tabel ini.

#### F. Penutup
Paragraf penutup standar: ucapan terima kasih, undangan klarifikasi jika ada.

---

### 4. Bagian yang **DIKOSONGKAN** (diisi manual oleh auditor)

Biarkan placeholder berikut tetap kosong dengan penanda jelas agar auditor mudah menemukannya di Word:
```
Nomor LHP   : [DIISI AUDITOR — dari SIMWAS]
Tanggal LHP : [DIISI AUDITOR]
Kepada Yth. : [DIISI AUDITOR — jabatan + unit + "di Jakarta"]
Tembusan    : [DIISI AUDITOR — jika ada]
Tanda Tangan: [DIISI AUDITOR]
```

Jika template memiliki halaman Nota Dinas pengantar: **biarkan halaman tersebut dengan placeholder `[DIISI AUDITOR]`** pada field yang perlu diisi (Nomor ND, Tanggal, Hal, Lampiran, Tanda Tangan). **Jangan menulis isi Nota Dinas** — auditor akan melengkapi sendiri di Word.

---

### 5. Simpan file

`_LHP/LHP-SUBSTANSI-[nomor-ST].docx`

---

### 5a. Jalankan QC otomatis (WAJIB sebelum minta SETUJU)

Sebelum menyerahkan draft LHP kepada auditor, jalankan QC validator untuk mengecek konsistensi bahasa keyakinan, placeholder `[DIISI AUDITOR]` hanya di field administratif, dan format Arial.

```bash
python3 audit-system-v4/scripts/qc_kkp_lhp.py penugasan/[folder-penugasan] --only lhp
```

Aturan hasil QC:

- **PASS** → lanjut ke Langkah 6 & 7 (update context + minta SETUJU).
- **FAIL** (mis. bahasa keyakinan tidak sesuai paradigma jenis pengawasan, placeholder `[DIISI AUDITOR]` muncul di luar field administratif, font bukan Arial pada area substansi) → perbaiki LHP, simpan ulang, jalankan QC lagi. **Jangan minta SETUJU sebelum QC PASS.**
- **Warning** → boleh lanjut, tapi sebutkan warning secara eksplisit di pesan ke auditor.

Tujuan QC: melindungi auditor dari kesalahan klise (mis. LHP reviu yang terlanjur memakai "pendapat kami memadai" yang menjanjikan keyakinan memadai).

---

### 6. Update context.md
```
Status        : TAHAP 2 — LHP SUBSTANSI (iterasi ke-[n])
File LHP Draft: _LHP/LHP-SUBSTANSI-[nomor-ST].docx
```

### 7. Konfirmasi kepada auditor (sekaligus penutup otomasi)

```
=== LHP SUBSTANSI DRAFT [iterasi ke-N] SELESAI ===
File       : _LHP/LHP-SUBSTANSI-[nomor-ST].docx
Catatan    : [N] catatan ([x] dengan rekomendasi, [y] sesuai)
Rekomendasi: [N] rekomendasi
QC auto    : PASS [/ PASS dengan [n] warning — sebut ringkasannya]

Bagian yang DIKOSONGKAN (diisi manual oleh Anda di Word):
  - Nomor dan tanggal LHP (dari SIMWAS)
  - Destinatari (Kepada Yth.) dan tembusan
  - Nota Dinas pengantar (format standar — lihat panduan-format-umum)
  - Tanda tangan Inspektur

Mohon baca dan beri feedback SUBSTANSI:
  - Apakah uraian kondisi/kriteria sudah tepat dan cukup?
  - Apakah rekomendasi sudah spesifik dan dapat dilaksanakan?
  - Ada bagian yang perlu ditambah atau direvisi?

Jika ada koreksi substansi → balas di chat, saya revisi (iterasi berikutnya).
Jika substansi DISETUJUI → ketik SETUJU.
  Setelah itu:
    1. Lengkapi nomor surat / tanggal / destinatari / Nota Dinas di Word (manual)
    2. Tanda tangani
    3. Kirim ke auditan

Otomasi sistem berhenti di sini. Terima kasih.
```

---

## ⛔ GATE — LHP Substansi harus disetujui auditor
- Auditor menyatakan substansi LHP sudah disetujui via chat (SETUJU)
- Semua koreksi substansi sudah diakomodasi
- Setelah SETUJU → otomasi selesai. Administrasi (Nota Dinas, nomor surat, TTD) dikerjakan auditor secara manual.

### 📋 Simpan Feedback LHP

Setelah auditor memberikan feedback (baik koreksi maupun persetujuan), simpan ke:
`audit-system-v4/feedback/[YYYY-MM-DD]-LHP-[nomor-ST].md`

Format file feedback:
```
# Feedback LHP — [nomor ST]
Tanggal     : [tanggal hari ini]
Obyek       : [nama obyek dari context.md]
Skill       : [nama skill]
Versi LHP   : [v1 / v2 / dst]

## Feedback Auditor
[Tulis verbatim atau ringkasan koreksi dari auditor]

## Aspek yang Dikoreksi
- [ ] Kondisi (uraian fakta)
- [ ] Kriteria (dasar hukum yang dikutip)
- [ ] Akibat/risiko
- [ ] Rekomendasi (spesifisitas, kelayakan, siapa yang bertanggung jawab)
- [ ] Simpulan
- [ ] Gambaran umum obyek
- [ ] Format/struktur laporan
- [ ] Lain-lain: [sebutkan]

## Tindak Lanjut
[Jelaskan perubahan yang dilakukan pada LHP sesuai feedback — atau "Disetujui tanpa koreksi"]

## Pelajaran untuk Sistem
[Jika ada pola masalah yang berulang atau hal baru yang ditemukan, catat di sini
 sebagai bahan perbaikan skill/template ke depan]
```

> Feedback LHP lebih berharga dari feedback KKP karena menunjukkan kualitas akhir analisis. Isi bagian "Pelajaran untuk Sistem" dengan jujur — ini yang akan digunakan untuk iterasi skill berikutnya.

---

## Jika Template Tidak Tersedia

Gunakan struktur standar:
```
A. PENDAHULUAN
   1. Latar Belakang
   2. Dasar Pelaksanaan
   3. Tujuan dan Sasaran
   4. Ruang Lingkup
   5. Metodologi
   6. Jangka Waktu Pelaksanaan
   7. Komposisi Tim

B. GAMBARAN UMUM OBYEK PENGAWASAN

C. HASIL PENGAWASAN
   [Sub-area → per catatan: Judul → Kondisi → Kriteria → Akibat → Rekomendasi]

D. SIMPULAN

E. REKOMENDASI
   [Tabel rekomendasi]

F. PENUTUP
```

---

## Panduan Formatting DOCX (wajib untuk edit template via XML/python-docx)

Jika mengedit template DOCX secara programatik (unpack XML atau python-docx), **selalu gunakan format berikut** agar konsisten dengan template resmi:

| Elemen | Nilai yang benar | Cara set di XML |
|--------|-----------------|-----------------|
| **Font** | `Arial` (bukan Times New Roman) | `w:rFonts w:ascii="Arial" w:hAnsi="Arial"` |
| **Alignment** | `both` (justified) | `w:jc w:val="both"` dalam `w:pPr` |
| **Font size** | `24` (=12pt) untuk isi teks | `w:sz w:val="24"` |
| **Ordering di pPr** | `jc` harus **sebelum** `rPr` | Jika `jc` muncul setelah `rPr`, pindahkan |

> **Mengapa ini penting**: Kesalahan font (Times New Roman vs Arial) dan alignment (None vs both/justified) membuat LHP terlihat tidak profesional dan berbeda dari template. Ini terdeteksi dari uji coba April 2026.

Jika menggunakan script Python untuk edit XML:
```python
# Fungsi standar untuk buat paragraf baru (selalu gunakan ini):
def make_para(text, bold=False, sz="24", jc="both"):
    """Buat paragraf dengan Arial, justified, sz=24 — default template resmi."""
    p = etree.Element(wt("p"))
    ppr = etree.SubElement(p, wt("pPr"))
    jc_el = etree.SubElement(ppr, wt("jc"))
    jc_el.set(wt("val"), jc)
    r = etree.SubElement(p, wt("r"))
    rpr = etree.SubElement(r, wt("rPr"))
    fonts = etree.SubElement(rpr, wt("rFonts"))
    fonts.set(wt("ascii"), "Arial"); fonts.set(wt("hAnsi"), "Arial")
    sz_el = etree.SubElement(rpr, wt("sz"))
    sz_el.set(wt("val"), sz)
    if bold: etree.SubElement(rpr, wt("b"))
    t = etree.SubElement(r, wt("t"))
    t.text = text; t.set(f"{XML_SPACE}space", "preserve")
    return p

# Fungsi fix format paragraf yang sudah ada (untuk normalisasi):
def fix_para_format(para):
    """Set font Arial + jc=both + pastikan ordering jc sebelum rPr."""
    ppr = para.find(wt("pPr"))
    if ppr is None:
        ppr = etree.SubElement(para, wt("pPr"))
        para.insert(0, ppr)
    # Tambah/update jc=both, pastikan posisi sebelum rPr
    rpr_el = ppr.find(wt("rPr"))
    jc = ppr.find(wt("jc"))
    if jc is None:
        jc = etree.Element(wt("jc"))
        if rpr_el is not None:
            ppr.insert(list(ppr).index(rpr_el), jc)
        else:
            ppr.append(jc)
    jc.set(wt("val"), "both")
    # Fix font di semua run
    for r in para.findall(f".//{wt('r')}"):
        rpr = r.find(wt("rPr"))
        if rpr is None: rpr = etree.SubElement(r, wt("rPr")); r.insert(0, rpr)
        fonts = rpr.find(wt("rFonts"))
        if fonts is None: fonts = etree.SubElement(rpr, wt("rFonts")); rpr.insert(0, fonts)
        fonts.set(wt("ascii"), "Arial"); fonts.set(wt("hAnsi"), "Arial")
```

## QC Kepatuhan SAIPI (v4 — WAJIB sebelum gate ketua tim)

Sesaat setelah `_LHP/LHP-SUBSTANSI-*.docx` ditulis dan SEBELUM minta konfirmasi ketua tim:

```bash
python3 scripts/qc_saipi.py --penugasan penugasan/[nama] --stage lhp
```

`qc_saipi.py --stage lhp` re-cek standar tahap KKP + tambah cek standar 2400 (komunikasi):
- KOM-001..004: heading wajib (Tujuan, Ruang Lingkup, Simpulan, Rekomendasi)
- KOM-005: tidak ada placeholder bocor (kecuali whitelist `[DIISI AUDITOR]`)
- KOM-007: ada section "Tanggapan Auditi/Manajemen/Klien"
- KOM-008: ada pernyataan "dilaksanakan sesuai dengan Standar Audit Intern Pemerintah Indonesia" (SAIPI 2430 — wajib)

Output:
- `_QA-SAIPI/checklist-lhp.json`
- `_QA-SAIPI/laporan-qa-lhp.md`
- 1 event audit-trail (`VALIDATION_PASSED` atau `VALIDATION_FAILED`)

**Aturan gate:**
- Exit 0 → tampilkan ringkasan singkat ke ketua tim, lanjut konfirmasi LANJUT/SETUJU.
- Exit 2 (ada KRITIS) → **JANGAN minta gate**. Tampilkan isi `laporan-qa-lhp.md`, koreksi LHP dulu, jalankan ulang qc_saipi.

> **Tujuan**: cegah berkas LHP submit ke INTEGRAL dengan gap kepatuhan yang sebenarnya bisa dikoreksi 5 menit.

---

## Finalisasi v4 (setelah ketua tim SETUJU LHP)

Setelah ketua tim memberi konfirmasi LANJUT/SETUJU pada draft LHP:

```bash
# 1. Mark semua temuan jadi DISETUJUI di temuan.json
#    (script bisa dibuat ad-hoc, atau edit JSON manual + validate ulang)
python3 scripts/validate_kkp_json.py penugasan/[nama]/_KKP/temuan.json

# 2. Log finalisasi
python3 scripts/audit_trail.py log-event --penugasan penugasan/[nama] \
  --action LHP_FINALIZED --task 04 --target _LHP/LHP-SUBSTANSI-[nomor].docx \
  --payload '{"jumlah_temuan": N, "iterasi": "v3"}'

# 3. (v4.2+) INTEGRAL_EXPORT sudah otomatis di-log saat Task 03 auto-inject.
#    Tidak perlu manual log lagi di sini. Untuk verifikasi:
grep INTEGRAL_EXPORT penugasan/[nama]/_AUDIT-TRAIL/events.jsonl
```

🆕 **Sejak v4.2 (10 Mei 2026):** `temuan.json` otomatis di-POST ke endpoint REST API INTEGRAL via `scripts/integral_inject.py` saat Task 03 berakhir (setelah anggota tim SETUJU). Auditor cukup login INTEGRAL, review KKP draft yang sudah masuk, lalu klik **Approve** untuk mengubah status dari `ai_draft` ke `auditor_approved`.

**Exception** untuk 4 jenis pengawasan (konsultasi-pengadaan, evaluasi-spip, evaluasi-reformasi-birokrasi, pemantauan-tindak-lanjut) — output format khusus, auditor tetap perlu upload manual menggunakan output di folder `_KKP/`. Untuk 4 jenis ini, log `INTEGRAL_EXPORT` perlu dijalankan manual setelah upload manual.

### Auto-Ingest ke Wiki (v4.0.2 — WAJIB setelah INTEGRAL_EXPORT)

Setelah event `INTEGRAL_EXPORT` ter-log (langkah sebelumnya), Claude **otomatis** memanggil:

```bash
python3 scripts/ingest_to_wiki.py --penugasan penugasan/[nama]
```

Script ini akan:
1. Buat halaman penugasan baru: `wiki/wiki/lhp-{slug-penugasan}.md` (snapshot temuan)
2. Re-aggregate `wiki/wiki/pattern-temuan.md` (gabungan v4 temuan + pattern-library lama)
3. Re-aggregate `wiki/wiki/database-kp.md` & `wiki/wiki/database-pkp.md`
4. Extract rekomendasi → `wiki/wiki/tlhp-index.md`
5. Update kriteria yg dirujuk → `wiki/wiki/references-index.md`
6. Update aggregat → `wiki/wiki/audit-trail-overview.md`
7. Append entry ke `wiki/wiki/log.md`
8. Tulis 1 event `INGEST_TO_WIKI` ke audit trail penugasan

> **Gate**: ingest hanya jalan kalau `LHP_FINALIZED` + `INTEGRAL_EXPORT` sudah ada di audit trail. Kalau ingest dipanggil sebelum kedua event itu, akan exit code 2 (ditunda). Bisa dipaksa dengan `--force`.

Bila auditor mau re-aggregate halaman wiki tanpa ingest penugasan baru:
```bash
python3 scripts/ingest_to_wiki.py --re-aggregate-only
```

## Catatan
- Task 04 dapat dijalankan **berkali-kali** — setiap iterasi menghasilkan versi baru (v2, v3, ...)
- Task 04 adalah **tahap akhir otomasi**. Setelah substansi disetujui, administrasi (nomor surat, tanggal, Nota Dinas, TTD) dikerjakan auditor manual di Word.
- LHP Substansi adalah dokumen **kerja siap finalisasi** — field administratif ditandai `[DIISI AUDITOR]`
- File yang sedang terbuka di Word tidak bisa di-overwrite dari bash — simpan ke nama `v2`, `v3`, dst.

---

## Panduan Cepat untuk Auditor — Administrasi Manual (eks-Task 05)

Setelah substansi LHP disetujui, auditor melengkapi 5 hal berikut di Word (±10–15 menit):

1. **Nomor LHP** di header LHP — ambil dari SIMWAS. Format: `B-[nomor]/IJ.3/[kode]/[bulan]/[tahun]`. Kode: `PW.04.04` (audit/reviu), `PW.04.05` (evaluasi), `PW.04.06` (pemantauan), `PW.04.07` (konsultasi).
2. **Tanggal LHP** di header + blok TTD.
3. **Destinatari (Kepada Yth.)** — jabatan + unit + "di Jakarta".
4. **Tembusan** — daftar penerima salinan (biasanya Irjen).
5. **Nota Dinas pengantar** — dokumen terpisah, format singkat:
   ```
   KOP SURAT
   NOTA DINAS
   Nomor : [nomor ND]
   Kepada Yth. : [jabatan]
   Dari        : Inspektur II
   Hal         : Laporan Hasil [Jenis] [Obyek] [Periode]
   Tanggal     : [tanggal]

   Menindaklanjuti [ST/ND Permintaan No. ... tanggal ...], kami telah
   melaksanakan [jenis] terhadap [obyek]. Bersama ini kami sampaikan
   laporan hasil [jenis] sebagaimana terlampir.

   [Jika ada link Survei SIMWAS: "Kami mohon kesediaan Saudara untuk
    mengisi survei kepuasan melalui: [link] (minimal 5 pegawai)."]

   Terima kasih atas perhatian dan kerja sama Bapak/Ibu.

                                   Jakarta, [tanggal]
                                   Inspektur II,


                                   [Nama]
                                   NIP [NIP]

   Tembusan: [daftar]
   ```
6. **Tanda tangan** — basah atau elektronik.

Setelah lengkap → kirim ke auditan via SIMWAS/persuratan.

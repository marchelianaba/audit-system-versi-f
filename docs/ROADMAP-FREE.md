# Roadmap INTEGRAL **FREE**

**Identitas.** Turunan ramping dari `v10.0-baseline` (repo `audit-system-v10`) untuk
**Inspektorat I, III, dan IV**, diintegrasikan ke `simwasv2.komdigi.go.id`.
Bukan untuk K/L lain.

> **Posisi produk — ASISTEN PERUMUSAN KKSA.**
> FREE **bukan** "agen yang mencari temuan dari tumpukan dokumen". Auditor melakukan
> analisis awalnya sendiri, lalu mengunggah **catatan/temuan awal dalam format apa pun**;
> agen membantu **merumuskannya menjadi KKSA & laporan yang baik dan sesuai standar**.
> Kemampuan analisis berat sengaja dikurangi — nilai tambahnya dipindah ke
> kelengkapan unsur, ketepatan sitasi pasal, dan kepatuhan format.

**Hubungan dengan artefak lain** (desain: `USULAN-DESAIN-2-TIER.html`):

| Artefak | Peran |
|---|---|
| ❄ **BEKU** `v10.0-baseline` / `v10.0.1` | induk; pembanding mutu |
| ⚡ **FULL** (`audit-system-v10`) | produk terpisah — **tidak lagi menjadi hulu** |
| 🌐 **FREE** (repo ini) | **berdiri sendiri** |

> **PISAH PENUH sejak 5 Agustus 2026.** Aturan lama "FREE hanya mencabut, tarik satu arah
> dari hulu" **DICABUT** atas keputusan pengguna. Remote `upstream` sudah dilepas.
> FREE kini boleh **menambah kemampuan sendiri**, dan FULL dikerjakan di sesi/repo terpisah.
> Konsekuensi yang harus disadari: perbaikan mesin di FULL **tidak lagi mengalir otomatis**
> ke sini — bila ada perbaikan yang layak dibawa, ambil manual dan catat asalnya.

---

## Fase 0 — Fondasi ✅ SELESAI

- **Fork dari titik beku** `v10.0-baseline`, **riwayat git dipertahankan** (bukan squash).
  Remote `upstream` dulu terpasang untuk tarik satu arah — **sudah dilepas 5 Agu 2026**
  saat kedua produk dipisah penuh.
- **Isolasi antar-Inspektorat** terbawa dari BEKU: `app/tenancy.py` (404 bukan 403, fail-closed),
  kolom `inspektorat` di User & Penugasan, 11 berkas rute disaring.
- **Injeksi wiki → skill (snapshot beku)** — **248 berkas**: 96 pattern · 114 konteks · 38 template.
  Skrip `backend/scripts/inject_wiki_to_skills.py` (`--apply` / `--revert`) ikut terbawa di repo ini;
  jalankan ulang bila ingin menyegarkan (butuh salinan wiki).

## Fase 1 — Ramping: murni alur penugasan ✅ SELESAI

- Tool agen: `WIKI_TOOLS` + `read_preload_context` dicabut → **28 tool, nol tool wiki**.
- Modul dihapus: `routes/knowledge.py`, `routes/chat.py`, `preload_context.py`,
  `wiki_promote.py`, `wiki_writeback.py`, `knowledge_browse.py`, `tools/wiki_tools.py`.
- Frontend: menu **Knowledge** (5 submenu) + **Chat AI** dihapus.
- Data `knowledge/wiki/` tidak disertakan (isinya sudah pindah ke skill).
- Bedah `routes/penugasan.py`: auto-build preload dihapus; `sasaran/templates` disisakan
  mode `historis` (fungsi peringkat di-*port* jadi mandiri).
- **Varian doktrin FREE** — `list_temuan_patterns` → `read_skill_reference(...90-pattern-temuan/README.md)`;
  `get_konteks(...)` → `references/90-konteks-organisasi/*.md`. **5/5 jalur terverifikasi ada & terbaca.**
- **Perbaikan keamanan** (ditemukan saat pengerjaan, sudah juga masuk FULL `v10.0.1`):
  query *pilih-kolom* tak tersaring (`sasaran/templates`, `dashboard`) + **cache dashboard global**
  → keduanya ditutup.

### Putaran kedua — CACM, graduasi, tulis-skill (4 Agu 2026)

Keputusan: FREE **murni alur penugasan**. Tiga hal berikut dicabut seluruhnya,
bukan disembunyikan:

| Dicabut | Cakupan | Alasan |
|---|---|---|
| **CACM / EWS SIRUP** | 4 modul + rute + 4 model DB + status `USULAN_CACM` + panel EWS beranda + halaman `/cacm` & `/cacm/kriteria` + menu + 24 metode klien + kriteria YAML | pengawasan berkelanjutan berbasis sinyal, bukan pelaksanaan penugasan |
| **Graduasi** | `app/graduasi.py`, rutenya, meta-skill, 5 metode klien | menyuling skill baru dari pola temuan = penyusunan pengetahuan; FREE tak ikut update wiki |
| **Tulis skill lewat API** | `PUT /skills/{slug}`, `POST /skills` → **405** | skill FREE dipatok allowlist 7 buah, diperbarui lewat **pengembang** (commit repo) |

Ikut dibersihkan — **sisa mati dari putaran pertama** yang masih memanggil endpoint
yang sudah tiada (404 saat dipakai pengguna): pemilih template KP/PKP wiki di
halaman penugasan, panel Konteks Pra-Loaded, dan 27 metode klien wiki/knowledge/
chat/preload.

**Hasil:** 48 endpoint tersisa, nol ber-prefiks `cacm`/`graduasi`/`knowledge`/`chat`/
`preload` · 39 tool agen tanpa satu pun tool wiki/CACM · 8 rute frontend
(Dashboard · Penugasan · Penugasan/[id] · Tindak Lanjut · Feedback Agen · Login).
Verifikasi: 84 panggilan GET × 3 peran → 0 galat 5xx · alur penugasan utuh
(buat penugasan 201, antrean HITL 2 temuan, 7 skill) · `tsc --noEmit` bersih ·
`next build` sukses.

## Fase 2 — Skema Asisten KKSA ✅ SELESAI

Inti nilai FREE. Rinciannya di `USULAN-DESAIN-2-TIER.html` §5.

- **Jenis dokumen baru `CATATAN-AUDITOR`** → subfolder `05-catatan-auditor`
  (berbeda dari `BUKTI-LAPANGAN` dan dari dokumen objek). Ingestion sudah siap:
  PDF · Word · Excel · teks + **OCR** untuk catatan hasil scan/foto.
- **Mode doktrin "SUSUN KKSA DARI CATATAN AUDITOR"** dengan pembagian peran per unsur:

  | Unsur | Sumber | Peran agen |
  |---|---|---|
  | Kondisi | **auditor** | rapikan jadi fakta spesifik — **tidak menambah fakta** |
  | Kriteria | **agen** | carikan pasal tepat dari 54 referensi bawaan + kutip presisi |
  | Sebab | auditor | bila tak ada → **"tidak cukup data"**, dilarang menyimpulkan |
  | Akibat | agen | konservatif, dari Kondisi × Kriteria |
  | Rekomendasi | agen (usulan) | keputusan tetap di KT |

- **Doktrin pengaman anti-"pemolesan"**: unsur tanpa dukungan **ditandai eksplisit**
  (*"belum didukung bukti — mohon auditor lengkapi"*), bukan diisi; dugaan tetap
  **bukan temuan**; tiap Kriteria wajib membawa kutipan pasal.
- **Batasi skill** (disepakati, mulai sempit): `reviu-pengadaan`, `reviu-rka-kl`,
  dan keluarga `*-umum`. Rezim LKE (SPIP/SAKIP/RB) tidak termasuk.
- **UI**: area unggah catatan auditor + penanda "Draf hasil analisis AI".

### DoD TERCAPAI — uji tuntas 4 Agu 2026

Satu penugasan `reviu-pengadaan` dijalankan penuh di basis data terpisah
(`integral_free`): catatan auditor `.docx` (4 butir, mutu sengaja dibuat berbeda)
→ agen AT 456 detik → KKP + QC SAIPI.

| Butir catatan | Mutu bahan | Hasil agen | Doktrin yang diuji |
|---|---|---|---|
| B1 HPS tanpa sumber harga | lengkap + Sebab dari keterangan PPK | **T-001** KKSA penuh, Kriteria = Perpres 16/2018 jo. 12/2021 **Ps. 26 ayat (5)** dikutip persis | nilai tambah Kriteria |
| B2 addendum tanpa BA | Kondisi kuat, Sebab **tidak ditelusuri** | **T-002**, Sebab = *"Tidak cukup data…"*, `kode_penyebab` kosong | **anti-mengarang** |
| B3 dugaan afiliasi penyedia | dugaan, belum diverifikasi | **BUKAN temuan** → `TIDAK_CUKUP_DATA` + usul verifikasi akta/AHU | **"diduga" bukan temuan** |
| B4 "administrasi kurang rapi" | kesan umum tanpa rincian | **BUKAN temuan** → `TIDAK_CUKUP_DATA` + minta rincian dokumen + pasal | **anti-"pemolesan"** |

Agen juga menandai sendiri satu Kriteria yang belum pasti:
*"[Auditor: mohon verifikasi nomor Bab/Pasal spesifik dalam Perlem LKPP 12/2021…]"* —
persis perilaku yang diminta doktrin, bukan menambal dengan pasal karangan.

- **QC SAIPI stage KKP: 16 OK · 0 KRITIS · 0 PERINGATAN · 3 NEEDS_REVIEW** → **LOLOS**.
  Ketiga NEEDS_REVIEW memang butuh konfirmasi manusia (deklarasi independensi,
  riwayat PIC, kebutuhan keahlian khusus).
- Kedua temuan berstatus **DRAFT/PENDING** di antrean HITL Ketua Tim. `KKP-Sari-Wijaya.docx` ter-render.
- Tiap unsur membawa `dokumen_sumber` (berkas + halaman + kutipan).

**Empat cacat ditemukan & diperbaiki saat uji ini** — lihat riwayat commit
`0e7e1db`, `5eaceba` (FREE) dan `a1629c7`, `780baaa` (hulu/FULL, lalu di-*cherry-pick*):
`POST /penugasan` hilang · `"tor"` cocok dengan "audi**tor**" · digest belum kenal
`05-catatan-auditor` · dua fungsi pembantu hilang (→ `GET /penugasan/{id}` dan
antrean HITL selalu 500). Regresi diuji: 96 panggilan GET × 3 peran → 0 galat 5xx.

## Fase 2B — Dual mode: 3 skema penyusunan KKSA ✅ SELESAI (5 Agu 2026)

Keputusan pengguna (4 Agu 2026): FREE punya **mode AI dan mode manual berdampingan**.
Gerbangnya sama untuk ketiganya — **begitu auditor menekan SUBMIT, KKSA masuk reviu
berjenjang ke Ketua Tim**. Cara KKSA itu tersusun tidak mengubah gerbangnya.

| # | Skema | Peran AI | Peran auditor |
|---|---|---|---|
| **1** | auditor unggah **dokumen** | menganalisis + menyusun KKSA dari nol | edit manual / iterasi |
| **2** | auditor unggah **dokumen + catatan** | membantu merumuskan KKSA, **tidak menggali temuan lagi** | edit manual / iterasi |
| **3** | auditor menyusun **KKSA manual** | tidak terlibat (atau hanya diminta bila auditor mau) | mengarang penuh sendiri |

### Kesiapan mesin — apa yang sudah ada, apa yang belum

**Sudah siap, dipakai bersama ketiga skema:**

| Kebutuhan | Yang sudah ada |
|---|---|
| Skema 1 | alur baku v10 — **berjalan** |
| Skema 2 | jenis `CATATAN-AUDITOR` + mode doktrin "SUSUN KKSA DARI CATATAN AUDITOR" — **lulus DoD Fase 2** |
| Edit manual | `PUT /penugasan/{id}/temuan-review/{tid}/edit` — AT/KT/PT/PM. Overlay disimpan di `TemuanReview.edited_fields`; `temuan.json` tetap sumber kebenaran; tiap perubahan **terekam log** |
| Hapus temuan | `DELETE /penugasan/{id}/temuan/{tid}` — AT/KT/PT/PM |
| Iterasi dengan AI | SSE `GET /agen/{nama}/stream` + `/attach` |
| **Gerbang submit** | `POST /penugasan/{id}/kkp/submit` (AT) → sasaran jadi `SELESAI_KKP` + `diajukan_oleh`/`diajukan_pada` → sentinel `kkp-at-done.flag` → status `KKP_AT_DONE` → **KT menyetujui per-sasaran (Tahapan 4) → Lembar Reviu KT/PT/PM** |

**Yang tadinya belum ada — SEKARANG SUDAH DIKERJAKAN:**

1. **Tidak ada endpoint BUAT temuan manual.** Yang tersedia hanya *edit* dan *hapus* temuan
   yang sudah ada. Penulisan temuan baru cuma bisa lewat tool agen `append_temuan`, yang
   tidak terekspos sebagai rute HTTP. **Skema 3 mustahil dijalankan sekarang.**
2. **`TemuanEditPayload` tidak memuat `sebab`, `rekomendasi`, dan `dokumen_sumber`** —
   hanya `judul_temuan`, `kondisi`, `kriteria`, `akibat`, `note`. Akibatnya, ketika agen
   menulis *"tidak cukup data"* pada Sebab (persis yang dituntut doktrin anti-mengarang),
   **auditor yang kemudian menemukan penyebabnya tidak punya jalan untuk mengisinya.**
   Ini menyandera ketiga skema, bukan hanya skema 3.
3. **Tidak ada penanda mode maupun asal-usul temuan.** Label *"Draf hasil analisis AI"*
   tidak boleh menempel pada temuan yang murni ditulis auditor.
4. **Formulir KKSA manual di UI belum ada** — yang ada baru edit inline atas temuan bikinan AI.

### Rancangan

- **Mode disimpan per sasaran, bukan per penugasan.** Satu penugasan realistis campur:
  sasaran A cukup manual, sasaran B minta bantuan AI. Menyimpan mode di tingkat penugasan
  akan memaksa auditor memilih terlalu dini.
- **Asal-usul melekat pada temuan** (`origin`: `AI` · `AI_DARI_CATATAN` · `MANUAL`) supaya
  pelabelan draf-AI jujur, dan supaya uji mutu Fase 4 bisa membandingkan mutu antar-asal.
- **Perluas `TemuanEditPayload`** dengan `sebab`, `rekomendasi`, `dokumen_sumber` —
  perbaikan ini berdiri sendiri dan sebaiknya **didahulukan** karena menutup cacat nyata.
- **Endpoint baru `POST /penugasan/{id}/temuan`** (AT) untuk menulis KKSA dari nol,
  memakai jalur upsert yang sama dengan agen supaya penomoran `T-00n` tidak bentrok.
- **Doktrin tidak dilonggarkan untuk mode manual**: kutipan sumber tetap wajib (formulir
  memaksa `dokumen_sumber`), QC SAIPI tetap berjalan sebelum submit, dan unsur yang belum
  didukung bukti tetap ditandai — bukan dibiarkan kosong diam-diam.

### ✅ Hasil eksekusi (5 Agu 2026)

**Ditambah:**

| Endpoint / berkas | Guna |
|---|---|
| `POST /penugasan/{id}/temuan` (AT) | tulis KKSA dari nol — skema 3 kini mungkin. `dokumen_sumber` **wajib ≥1** dan tiap entri wajib `file` + `halaman`; dilanggar → **422** |
| `POST /penugasan/{id}/kkp/render` (AT) | render `KKP.docx` **tanpa sesi agen** — tanpa ini mode manual mustahil memenuhi LAK-007 |
| `origin` pada temuan | `AI` · `AI_DARI_CATATAN` · `MANUAL`, tampil sebagai lencana di UI |
| `mode` pada sasaran | `AI` / `CATATAN` / `MANUAL`, dipilih KT di PKP — **arahan, bukan kunci** |
| Formulir KKSA manual + kolom Sebab di UI | auditor menulis & melengkapi sendiri |

**Empat cacat yang ketahuan saat menguji dan ikut ditutup:**

1. `TemuanEditPayload` tak punya `sebab`/`dokumen_sumber`/kodefikasi → ketika agen menulis
   Sebab *"tidak cukup data"* sesuai doktrin anti-mengarang, auditor yang **kemudian**
   menemukan penyebabnya **buntu**. Menyandera ketiga skema.
2. Penomoran id memakai `len()+1` → hapus T-001, temuan berikutnya jadi T-002 yang sudah ada
   → **temuan lama tertimpa diam-diam** lewat UPSERT. Kini `max+1`, diuji 7 kasus.
3. `id_temuan_terkait` **tidak pernah diisi jalur mana pun**, hanya diperiksa QC → LAK-009
   menyala di semua penugasan. Kini diturunkan saat submit dari `sasaran_id` tiap temuan.
4. `context.md` scaffold tak punya bagian **Ruang Lingkup** yang diperiksa REN-005.

**DoD TERCAPAI** — satu penugasan berisi tiga temuan dari tiga skema berbeda:

| Temuan | Sasaran | `mode` | `origin` |
|---|---|---|---|
| T-001 | S-03 | MANUAL | `MANUAL` |
| T-002 | S-01 | AI | `AI` |
| T-003 | S-02 | CATATAN | `AI_DARI_CATATAN` |

Ketiganya ter-submit dalam **satu kali gerbang** (3 sasaran → `SELESAI_KKP`,
`id_temuan_terkait` terisi, status `KKP_AT_DONE`), dan **QC SAIPI: 16 OK · 0 KRITIS ·
0 PERINGATAN** (sisa 3 NEEDS_REVIEW memang tak bisa dicek otomatis). Sebab hasil editan
auditor terbukti ter-render di `KKP.docx` — bukan versi agen. `tsc --noEmit` bersih,
`next build` sukses.

## Fase 3 — Efisiensi & pagar biaya

- Model hemat + batas giliran agen; penilaian per-aspek & inkremental tetap nonaktif.
- **Kuota per Inspektorat per bulan** + laporan pemakaian (saat ini baru ada batas per jam/pengguna).
- Label tetap pada keluaran: *"Draf hasil analisis AI — wajib diverifikasi auditor berwenang."*
- **DoD:** biaya per penugasan **terukur** (bukan estimasi) dan berada di plafon yang direncanakan.

## Fase 4 — Uji mutu

- **Uji banding FREE vs BEKU** pada **objek yang sama** → ukuran nyata "seberapa kurang pintar",
  sekaligus bahan menjelaskan keterbatasan kepada pengguna.
- Uji skema KKSA dengan **catatan auditor nyata** (bukan sintetis), termasuk catatan
  yang sengaja tidak lengkap → memastikan agen **menandai**, bukan mengarang.
- **DoD:** doktrin anti-mengarang & anti-pemolesan terbukti dipatuhi.

## Fase 5 — Integrasi SIMWAS v2

- **SSO OIDC** (kini masih login peran untuk pengembangan) + pemetaan peran AT/KT/PT.
- Sinkronisasi **ST & sasaran** dari SIMWAS (endpoint sudah ada, masih memakai contoh).
- **Pilot 1 Inspektorat** yang bersedia.
- **DoD:** satu penugasan tuntas end-to-end dari SIMWAS tanpa intervensi manual.

## Fase 6 — Buka bertahap

- Tambah Inspektorat bertahap sambil memantau kuota, antrean, dan mutu.
- Siapkan dukungan pengguna (FAQ + kanal terbatas).

---

## Batas yang TIDAK boleh diturunkan

Berlaku sama seperti FULL — justru **makin penting** karena FREE dipakai di luar
kendali langsung tim Inspektorat II:

1. **Anti-mengarang** — Sebab hanya bila terbukti; jika tidak: "tidak cukup data".
2. **"Perlu diverifikasi/diduga" bukan temuan.**
3. **Kutipan sumber wajib** (nama dokumen + halaman/pasal).
4. **HITL wajib** — temuan berstatus DRAFT sampai auditor menyetujui.
5. **QC SAIPI tetap berjalan.**
6. **Label keluaran** sebagai draf AI.

## Keputusan yang masih terbuka

| # | Pertanyaan |
|---|---|
| 1 | Besaran kuota per Inspektorat per bulan |
| 2 | Siapa menanggung biaya API FREE |
| 3 | Model dukungan pengguna |

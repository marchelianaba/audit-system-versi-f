# Peta Blok PK — LKE SPIP rev4 2025 (Kementerian/Lembaga)

> **Sumber kebenaran: template `templates/lke-spip-kementerian.xlsx` (28 sheet, multi-satker).**
> Seluruh angka di dokumen ini **diukur langsung dari template**, bukan disalin dari
> dokumen versi sebelumnya. Struktur LKE **pra-rev4 sudah tidak dipakai**.

## Prinsip utama — deteksi DINAMIS, bukan koordinat hafalan

Jangan menghafal koordinat cell. Jumlah baris **berbeda tiap satker** (bergantung
banyaknya sasaran/unsur yang diisi auditee), sehingga koordinat statis pasti meleset.

**Alur yang benar:**

```
read_lke(skill="evaluasi-spip")                        → daftar sheet
read_lke(skill=…, sheet="<sheet>", fokus=1)            → baris hidup + blok pm/pk
fill_lke(skill=…, entries=[{sheet, coord, value}])     → tulis ke koordinat blok `pk`
```

`fokus=1` mengembalikan, per baris data hidup: `uraian` (kolom B), blok **`pm`**
(nilai auditee), blok **`pk`** (kolom APIP — koordinat siap dipakai `fill_lke`),
dan `pk_terisi`. Tabel di bawah hanya **orientasi** — yang dipakai tetap hasil
`fokus=1` saat runtime.

## Struktur baris (berlaku semua sheet detail)

| Baris | Isi |
|---|---|
| 1–2 | judul kertas kerja (`='NAMA SATKER'!C3`, nama KK) |
| 3 | **label blok**: `PM` · `PK` · `EVALUASI` |
| 4 | nama kolom per blok |
| 5 | nomor kolom (1, 2, 3, …) |
| 6+ | **data** — baris hidup ditandai **kolom B terisi** |

**APIP mengisi blok `PK` saja.** Blok `PM` milik auditee, blok `EVALUASI` milik
evaluator lain — keduanya jangan disentuh.

## Peta blok per sheet (terukur dari template)

| Batch | Sheet | Baris header | Kolom PM | **Blok PK** | Keterangan |
|---|---|---|---|---|---|
| I | `KKE 1 SASTRA` | 3 | F | **U–AI** | Penetapan Tujuan — Sasaran Strategis K/L |
| I | `KKE 2.1 SASPRO` | 3 | I | **AC–AV** | Sasaran Program |
| I | `KKE 2.2 SASKEG` | 3 | M | **AG–AZ** | Sasaran Kegiatan |
| I | `KKE 2.3 SAS RO` | 3 | O | **AD–AR** | Rincian Output |
| II | `KK3.1` | 3 | CQ | **CY–DF** | Struktur & Proses — dimensi efektivitas |
| II | `KK3.2` `KK3.3` `KK3.4` | — | — | *(tanpa blok PK)* | panduan-saja — tak memblokir render |
| III | `KK 5.1 A` | 3 | D | **N–W** | Pencapaian Tujuan SPIP |
| III | `KK 5.1 B` | 3 | H | **S–AC** | Pencapaian Tujuan SPIP |
| III | `KK 5.2` | 3 | K | **T–AB** | Pencapaian Tujuan SPIP |
| III | `KK 6` `KK 7` `KK 8` | — | — | *(tanpa blok PK)* | panduan-saja |
| III | `KK 4` | 3 | — | **C–E** | Penalti/pengurangan nilai (lihat bawah) |

> Sheet "panduan-saja" **tetap ditelaah**, tetapi ketiadaan blok PK di dalamnya
> tidak menjadi alasan `render_kkp_docx` diblokir (lihat `lke_batch_status`).

## Sheet agregator — HANYA BACA

`KKLEAD_SPIP` · `KKLEAD I` · `KKLEAD II` · `KKLEAD III`

Seluruhnya terhitung otomatis dari rumus. `fill_lke`/`LKEWriter` **menolak**
penulisan ke sheet ini (dan ke cell bertipe formula di sheet mana pun) secara
runtime lewat `cell.data_type == "f"` — hasil penolakan dilaporkan di field
`refused`. Rumus template tidak pernah berubah.

## Penalti / veto — mekanisme rev4

Sheet **`KK 4`** ("KERTAS KERJA PENALTI/PENGURANGAN NILAI") punya **dua blok**:

| Blok | Kolom | Isi | Pengisi |
|---|---|---|---|
| **PK** | **C** = PENGURANGAN NILAI (veto YA/TIDAK) · **D** = GRADASI PENURUNAN LEVEL · **E** = HASIL ANALISIS PENJAMINAN KUALITAS | **APIP** ← isi di sini |
| EVALUASI | F = PENGURANGAN NILAI · G = GRADASI PENURUNAN LEVEL · H = HASIL ANALISIS EVALUASI | evaluator lain — jangan disentuh |

Baris 6 = nama unsur (mis. "Lingkungan Pengendalian"), baris 7+ = sub-unsur.

**Rumus konsumen di `KKLEAD II` (terverifikasi di template):**

```
KKLEAD II!R6  = 'KK 4'!C7      ← kolom berlabel "VETO (YA/TIDAK)"
KKLEAD II!S6  = 'KK 4'!D7      ← "GRADASI PENURUNAN LEVEL"
KKLEAD II!AA6 = 'KK 4'!F7      ← blok EVALUASI (bukan ranah APIP)
KKLEAD II!AB6 = 'KK 4'!G7
```

Perhatikan **pergeseran baris**: `KKLEAD II` baris 6 membaca `KK 4` baris 7.
Jangan mengasumsikan baris sejajar — telusuri lewat `read_lke(..., fokus=1)`.

**Cara menerapkan penalti:** cukup isi blok PK `KK 4` (kolom **C** veto,
**D** gradasi, **E** dasar analisis) pada baris sub-unsur terkait. Nilai agregat
di `KKLEAD II` menyesuaikan otomatis — **jangan** menurunkan skor manual di `KK3.x`.

## Aturan penulisan (ringkas)

1. Tulis **hanya** ke koordinat di blok `pk` hasil `read_lke(..., fokus=1)`.
2. Jangan sentuh blok `PM`, blok `EVALUASI`, sheet `KKLEAD*`, dan cell formula.
3. Semua penulisan lewat **`fill_lke`** — jangan memanipulasi openpyxl langsung.
4. Output = salinan kerja **`_KKP/LKE-terisi-evaluasi-spip.xlsx`**; berkas asli
   / template tidak pernah diubah.
5. Sheet besar dikerjakan **per batch** (KK Lead I/II/III), satu batch per run —
   pantau lewat `lke_batch_status`.

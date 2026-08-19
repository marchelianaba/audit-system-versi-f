<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-pengadaan/PMP-55-sirup-draft-tinggi.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PMP-55
skill: pemantauan-pengadaan
kategori: PBJ-SIRUP
severity: HIGH
judul: "Pagu SIRUP Status Draft Tinggi Mendekati Pelaksanaan"
kriteria_baku: "Perpres 16/2018 Pasal 22 + Peraturan LKPP tentang RUP"
tags: [sirup, rup, draft, perencanaan-pengadaan, crunch-time, pemantauan-pengadaan]
---

# PMP-55: Pagu SIRUP Status Draft Tinggi Mendekati Pelaksanaan

## Pattern Kondisi

Persentase pagu di SIRUP masih berstatus *draft* tinggi meskipun sudah mendekati/melewati awal periode pelaksanaan. Indikator umum:

- Pagu draft >50% setelah akhir TW I (mis. 68,36% per 27 Jan)
- Paket risiko tinggi masih draft (mis. TKPPSE/CSE/ISP)
- SIRUP tidak konsisten dengan RKA-K/L
- Tidak ada milestone tracking finalisasi paket

## Kriteria

Perpres 16/2018 Pasal 22 + Peraturan LKPP RUP — RUP wajib diumumkan/difinalisasi di awal TA; pagu draft yang bertahan menandakan perencanaan pengadaan belum matang.

## Akibat

1. Eksekusi pengadaan mundur ke TW III/IV (*crunch time*)
2. Risiko gagal serap/realisasi rendah
3. Kualitas pemilihan menurun karena terburu-buru

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| SIRUP (status paket) | % pagu draft vs final |
| RKA-K/L | konsistensi dengan SIRUP |
| Daftar paket risiko tinggi | status draft paket besar |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PMP-55",
  "assigned_to": "{nama anggota}",
  "judul": "Pagu SIRUP {satker} {X}% Masih Draft per {tgl}",
  "kondisi": "Pemantauan SIRUP {satker} per {tgl}: {X}% pagu (Rp{nilai}) masih berstatus draft; {N} paket risiko tinggi (mis. TKPPSE Rp.., CSE Rp.., ISP Rp..) belum final; SIRUP tidak konsisten dengan RKA-K/L.",
  "kriteria": "Perpres 16/2018 Pasal 22 + Peraturan LKPP RUP — RUP wajib difinalisasi di awal TA; pagu draft bertahan = perencanaan belum matang.",
  "akibat": "Eksekusi mundur ke TW III/IV (crunch time); risiko gagal serap; kualitas pemilihan menurun.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "68,36% pagu draft per 27 Jan 2026 ..."}]
}
```

## Contoh Kasus Historis

- **LHP Pengadaan Program Prioritas Wasdig 2026** — **68,36% pagu draft** di SIRUP per 27 Januari 2026 (Rp236,7M); 3 paket risiko tinggi Rp95M (TKPPSE Rp76M, CSE Rp6,9M, ISP Rp12M). Lihat [[lhp-pengadaan-program-prioritas-wasdig-2026]], [[pattern-temuan]] P-19.

## Catatan

- Sama dengan [[reviu-pengadaan/RP-11-pagu-sirup-draft-akhir-tw1]] (sisi reviu); pattern ini fokus pemantauan berkala.
- Rekomendasi: *early flag* TW I untuk paket draft >50%; sinkronkan SIRUP-RKA.

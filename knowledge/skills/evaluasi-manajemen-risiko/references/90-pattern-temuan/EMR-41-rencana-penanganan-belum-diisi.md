<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-manajemen-risiko/EMR-41-rencana-penanganan-belum-diisi.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: EMR-41
skill: evaluasi-manajemen-risiko
kategori: MR-PENANGANAN
severity: HIGH
judul: "Rencana Penanganan Risiko Belum Diisi (Risiko Strategis)"
kriteria_baku: "Pedoman MR K/L (komponen penanganan risiko)"
tags: [mr, penanganan-risiko, risiko-strategis, mitigasi, evaluasi-mr]
---

# EMR-41: Rencana Penanganan Risiko Belum Diisi

## Pattern Kondisi

Rencana Penanganan/Tindak Risiko belum diisi meskipun profil & peta risiko sudah ada. Indikator umum:

- Komponen Penanganan Risiko kosong (formulir tidak terisi)
- Risiko strategis teridentifikasi tetapi tidak ada opsi mitigasi/PIC/target waktu
- Profil risiko lengkap tetapi tindak lanjut tidak terstruktur
- Berlaku di level pemilik risiko tertinggi (Menteri)

## Kriteria

Pedoman MR K/L — setiap risiko (terutama strategis) wajib disertai rencana penanganan (opsi, mitigasi, PIC, target waktu) sebagai bagian siklus MR.

## Akibat

1. Risiko strategis tidak dikelola aktif/terstruktur
2. Pengendalian internal melemah
3. Skor maturitas MR turun

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Form penanganan risiko | terisi opsi/mitigasi/PIC/target |
| Profil & peta risiko | risiko strategis teridentifikasi |
| SIMR | status komponen Penanganan |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-EMR-41",
  "assigned_to": "{nama anggota}",
  "judul": "Rencana Penanganan Risiko {satker} Belum Diisi",
  "kondisi": "Evaluasi MR {periode} {satker}: Profil & Peta Risiko lengkap, namun Rencana Penanganan Risiko belum diisi (opsi/mitigasi/PIC/target waktu kosong). Risiko strategis belum dikelola aktif.",
  "kriteria": "Pedoman MR K/L — setiap risiko strategis wajib disertai rencana penanganan (opsi, mitigasi, PIC, target waktu).",
  "akibat": "Risiko strategis tidak dikelola terstruktur; pengendalian internal melemah; skor maturitas MR turun.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "Penanganan Risiko: belum diisi ..."}]
}
```

## Contoh Kasus Historis

- **ND-127 LHE MR Kemkomdigi (Menteri) TW I 2026** — Rencana Penanganan Risiko belum diisi (formulir kosong); Pemantauan TW I & Piagam Risiko juga belum; skor **40% "Perlu Perhatian"** (2 dari 5 komponen). Lihat [[nota-dinas-ir2-april-2026]] (ND-127), [[pattern-temuan]] P-33.

## Catatan

- Sinergi: [[evaluasi-spip/ESP-36-register-risiko-strategis-belum-ada]] (MRI bagian SPIP).
- Rekomendasi: susun + input Rencana Penanganan Risiko strategis lengkap.

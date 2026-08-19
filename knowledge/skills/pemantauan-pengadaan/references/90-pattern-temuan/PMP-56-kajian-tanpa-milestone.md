<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-pengadaan/PMP-56-kajian-tanpa-milestone.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PMP-56
skill: pemantauan-pengadaan
kategori: PBJ-PERENCANAAN
severity: MEDIUM
judul: "Kajian Selesai Tapi Belum Diturunkan ke Milestone Implementasi"
kriteria_baku: "Perpres 16/2018 Pasal 18 (perencanaan pengadaan)"
tags: [kajian, redesain, milestone, implementasi, rencana-aksi, pemantauan-pengadaan]
---

# PMP-56: Kajian Selesai Tapi Belum Diturunkan ke Milestone Implementasi

## Pattern Kondisi

Kajian/redesain teknis telah/akan selesai tetapi belum diturunkan ke rencana aksi konkret dengan milestone, sehingga eksekusi tertunda. Indikator umum:

- Kajian selesai tetapi eksekusi mundur ke TA berikutnya
- Tidak ada rencana aksi dengan milestone + PIC
- "Akan dilanjutkan" tanpa jadwal konkret
- Tidak ada SK Tim Implementasi yang menyertai kajian

## Kriteria

Perpres 16/2018 Pasal 18 — perencanaan pengadaan harus menghasilkan rencana yang dapat dieksekusi; hasil kajian wajib diturunkan ke rencana aksi operasional.

## Akibat

1. Hasil kajian menjadi "dokumen mati"
2. Eksekusi tertunda lintas-TA
3. Anggaran/aset terkait berisiko idle (lihat [[audit-kinerja/AK-17-sistem-pengendalian-bypass]])

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Dokumen kajian/redesain | status penyelesaian |
| Rencana aksi/implementasi | milestone + PIC ada? |
| SK Tim Implementasi | ada/tidak |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PMP-56",
  "assigned_to": "{nama anggota}",
  "judul": "Kajian {topik} Belum Diturunkan ke Milestone Implementasi",
  "kondisi": "Pemantauan {pengadaan}: kajian {topik} {selesai/akan selesai} {tgl}, namun belum diturunkan ke rencana aksi dengan milestone + PIC; eksekusi mundur ke TA {berikutnya}; tidak ada SK Tim Implementasi.",
  "kriteria": "Perpres 16/2018 Pasal 18 — perencanaan harus menghasilkan rencana yang dapat dieksekusi; kajian diturunkan ke rencana aksi operasional.",
  "akibat": "Hasil kajian jadi dokumen mati; eksekusi tertunda lintas-TA; anggaran/aset berisiko idle.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "kajian TW II 2026, eksekusi TA 2027 ..."}]
}
```

## Contoh Kasus Historis

- **LHP Pengadaan Redesain TKPPSE 2026** — kajian teknis redesain baru akan dikaji TW II 2026, eksekusi TA 2027; belum ada rencana aksi konkret dengan milestone. Lihat [[lhp-pengadaan-redesain-tkppse-2026]], [[pattern-temuan]] P-31.

## Catatan

- Sama dengan [[reviu-pengadaan/RP-12-kajian-tanpa-rencana-aksi]] (sisi reviu); pattern ini fokus pemantauan progres.
- Rekomendasi: rekomendasi setingkat *rencana aksi dengan milestone* + SK Tim Implementasi bersamaan kajian.

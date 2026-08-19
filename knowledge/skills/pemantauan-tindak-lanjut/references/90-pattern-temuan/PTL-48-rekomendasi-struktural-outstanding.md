<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-tindak-lanjut/PTL-48-rekomendasi-struktural-outstanding.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PTL-48
skill: pemantauan-tindak-lanjut
kategori: TLHP-STRUKTURAL
severity: HIGH
judul: "Rekomendasi Struktural Outstanding >2 Tahun (Butuh Regulasi/MoU Lintas K/L)"
kriteria_baku: "UU 15/2004 Pasal 20 + Pedoman Pemantauan TLHP"
tags: [tlhp, outstanding, struktural, mou-lintas-kl, regulasi, pemantauan-tl]
---

# PTL-48: Rekomendasi Struktural Outstanding >2 Tahun

## Pattern Kondisi

Rekomendasi BPK/APIP berstatus "Belum Sesuai" berlarut karena bersifat **struktural** — penyelesaiannya butuh regulasi baru/MoU lintas K/L, bukan aksi internal satker. Indikator umum:

- Satu rekomendasi di-TL ≥7 kali tanpa closure
- Substansi memerlukan MoU dengan K/L lain (BSSN/OJK/Polri/PPATK/APJII/LKPP)
- Regulasi pelaksanaan (PP/Permen/SE) belum terbit
- Cluster rekomendasi sejenis menumpuk di satu mitra

## Kriteria

UU 15/2004 Pasal 20 — TL rekomendasi selambatnya 60 hari setelah LHP diterima; Pedoman Pemantauan TLHP mengklasifikasikan status Sesuai/Belum Sesuai/Tidak Dapat Ditindaklanjuti.

## Akibat

1. Outstanding finansial & administratif menumpuk (mis. Rp200,89M)
2. Opini/kinerja mitra berisiko turun pada audit berikutnya
3. Pemborosan sumber daya pemantauan berulang

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Rekap TLHP (Simwas) | jumlah kali TL per rekomendasi |
| Matriks rekomendasi | klasifikasi: internal vs butuh regulasi/MoU |
| Status MoU/regulasi | ada/tidak draft + jadwal |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PTL-48",
  "assigned_to": "{nama anggota}",
  "judul": "{N} Rekomendasi Struktural BPK Outstanding >2 Tahun di {mitra}",
  "kondisi": "Rekap TLHP {periode}: {N} rekomendasi Belum Sesuai dengan TL ≥7×, bersifat struktural (butuh {regulasi/MoU K/L}). Outstanding finansial Rp{X}. Cluster: {arsitektur TKPPSE/ISP/MoU APJII/PDP}.",
  "kriteria": "UU 15/2004 Pasal 20 + Pedoman Pemantauan TLHP — TL wajib tuntas; rekomendasi struktural perlu eskalasi level Menteri.",
  "akibat": "Outstanding menumpuk; kinerja/opini mitra berisiko turun; sumber daya pemantauan terbuang.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "38 rek Belum Sesuai, Rp200,89M ..."}]
}
```

## Contoh Kasus Historis

- **TLHP Eksternal Simwas IR2** — 38 rekomendasi Belum Sesuai (**Rp200,89M** outstanding); cluster TKPPSE/ISP/MoU APJII/PDP, TL ≥7×; keamanan siber BSSN 2 rek 0 sesuai setelah 10-11 TL. Lihat [[tlhp-eksternal-simwas-ir2]], [[tlrhp-bpk-semester-2-2025]], [[pattern-temuan]] P-25.

## Catatan

- Rekomendasi: *escalation matrix by complexity* (internal vs lintas-K/L); MoU prioritas BSSN/LKPP/APJII/OJK/Polri/PPATK.
- Sinergi: PTL-49 (asimetri), [[kepatuhan-saipi/README]] (penguatan kelembagaan).

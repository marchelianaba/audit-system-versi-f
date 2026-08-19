<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-tindak-lanjut/PTL-52-outstanding-belum-disetor.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: PTL-52
skill: pemantauan-tindak-lanjut
kategori: TLHP-FINANSIAL
severity: HIGH
judul: "Outstanding Finansial Belum Disetor ke Kas Negara"
kriteria_baku: "UU 15/2004 + tindak lanjut rekomendasi (penyetoran kerugian negara)"
tags: [tlhp, setor-kas-negara, outstanding-finansial, kerugian-negara, pemantauan-tl]
---

# PTL-52: Outstanding Finansial Belum Disetor ke Kas Negara

## Pattern Kondisi

Rekomendasi yang mensyaratkan penyetoran ke kas negara belum dipenuhi (outstanding finansial). Indikator umum:

- Nilai temuan rekomendasi penyetoran belum disetor
- Sudah lewat batas waktu TL tetapi belum ada bukti setor (SSBP/SSPB)
- Outstanding terkonsentrasi pada beberapa kasus (mis. kolokasi, Metro-E, penarikan kas)
- Vendor dispute menghambat penyetoran (mis. gugatan PT SUFI)

## Kriteria

UU 15/2004 + ketentuan tindak lanjut rekomendasi — rekomendasi penyetoran kerugian/kelebihan negara wajib dipenuhi dengan bukti setor (SSBP/SSPB) dalam batas waktu.

## Akibat

1. Penerimaan/pengembalian negara tertunda
2. Rekomendasi tetap "Belum Sesuai"
3. Potensi kerugian negara permanen jika kedaluwarsa

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Rekap outstanding finansial | nilai per kasus |
| Bukti setor (SSBP/SSPB) | ada/tidak |
| Status dispute/gugatan | hambatan penyetoran |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-PTL-52",
  "assigned_to": "{nama anggota}",
  "judul": "Outstanding Finansial Rp{X} {mitra} Belum Disetor ke Kas Negara",
  "kondisi": "Pemantauan TLHP {periode} {mitra}: outstanding finansial Rp{X} (mis. kolokasi Rp.., Metro-E Rp.., penarikan kas Rp..) belum disetor; sudah lewat batas waktu TL tanpa bukti SSBP/SSPB; sebagian terhambat dispute {vendor}.",
  "kriteria": "UU 15/2004 + tindak lanjut rekomendasi — penyetoran kerugian/kelebihan negara wajib dipenuhi dengan bukti setor.",
  "akibat": "Penerimaan/pengembalian negara tertunda; rekomendasi tetap Belum Sesuai; potensi kerugian permanen.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "outstanding Wasdig ~Rp91,9M ..."}]
}
```

## Contoh Kasus Historis

- **Pemantauan TLHP Wasdig November 2025** — outstanding finansial internal **~Rp91,9M** (kolokasi Rp4,66M + Metro-E Rp34,70M + penarikan kas Rp27,6M + warisan JAR Rp2,3M); sebagian terhambat dispute PT SUFI (perkara 846/Pdt.G/2025). Lihat [[pemantauan-tlhp-wasdig-november-2025]], [[tlhp-internal-simwas-ir2]].

## Catatan

- Rekomendasi: percepat penyetoran dengan bukti SSBP/SSPB; selesaikan dispute paralel.
- Sinergi: [[audit-pengadaan/AP-26-pembayaran-retroaktif-syarat-lkpp]] (akar OM TKPPSE).

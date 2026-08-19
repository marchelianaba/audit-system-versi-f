<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/AP-29-kurs-klasifikasi-akun.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AP-29
skill: audit-pengadaan
kategori: PBJ-PEMBAYARAN
severity: MEDIUM
judul: "Kesalahan Kurs/Klasifikasi Akun pada Pembayaran"
kriteria_baku: "Perjanjian (klausul kurs) + SAP + ketentuan kurs JISDOR"
tags: [kurs, jisdor, satria, klasifikasi-akun, belanja-modal, audit-pengadaan]
---

# AP-29: Kesalahan Kurs/Klasifikasi Akun pada Pembayaran

## Pattern Kondisi

Pembayaran salah hitung akibat penggunaan kurs yang tidak sesuai perjanjian, atau salah klasifikasi akun belanja. Indikator umum:

- Konversi valas memakai kurs **tanggal rekonsiliasi**, bukan **tanggal penerbitan tagihan** (sesuai perjanjian)
- Belanja yang seharusnya **Aset/Belanja Modal (akun 53)** dianggarkan sebagai **Belanja Barang/Jasa (akun 52)**
- *Availability Payment* (AP) salah dasar perhitungan kurs
- Invoice valas tidak mencantumkan kurs acuan + tanggal

## Kriteria

Perjanjian (klausul kurs, mis. Lampiran KPBU) + SAP + ketentuan kurs JISDOR BI — konversi valas mengikuti kurs pada tanggal yang diperjanjikan; klasifikasi akun mengikuti sifat output (jasa vs aset).

## Akibat

1. Kelebihan/kekurangan pembayaran (mis. SATRIA Rp1,51M)
2. Salah saji Laporan Keuangan (akun salah, aset tidak tercatat)
3. Temuan BPK + koreksi

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Perjanjian/KPBU (lampiran kurs) | tanggal acuan kurs yang diperjanjikan |
| Berita Acara Rekonsiliasi | kurs yang dipakai vs seharusnya |
| RKA/akun belanja | kesesuaian akun 52 vs 53 dengan output |
| Pencatatan aset/KDP | aset tercatat dengan benar |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AP-29",
  "assigned_to": "{nama anggota}",
  "judul": "Kelebihan Pembayaran Rp{X} {pekerjaan} Akibat {Kesalahan Kurs/Klasifikasi Akun}",
  "kondisi": "Pembayaran {pekerjaan}: konversi valas memakai kurs JISDOR tanggal {rekonsiliasi} padahal perjanjian mensyaratkan tanggal {penerbitan tagihan}, menghasilkan selisih Rp{X}. / Belanja {item} Rp{Y} salah diklasifikasi akun 52 (Barang/Jasa) padahal output berupa aset (akun 53).",
  "kriteria": "Perjanjian (klausul kurs) + SAP + ketentuan kurs JISDOR — kurs mengikuti tanggal diperjanjikan; akun mengikuti sifat output.",
  "akibat": "Kelebihan/kekurangan pembayaran; salah saji LK; temuan BPK + koreksi.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **BPK SPI LK 2024 / Temuan SATRIA** — kurs JISDOR tanggal rekonsiliasi (bukan tanggal penerbitan tagihan BUP) → kelebihan **Rp1,51M** *availability payment* (Perjanjian KPBU 372/M.KOMINFO/5/2019 Lampiran 8). Salah klasifikasi akun: 4 paket (Jasa Konsultansi Pengawasan, Helikopter BTS 4G, PMO BTS 4G) Rp84,95M seharusnya akun aset. Lihat [[bpk-temuan-pdns-satria-2024]], [[bpk-spi-lk-kominfo-2024]].

## Catatan

- Rekomendasi: template invoice valas wajib cantumkan kurs + tanggal acuan; pelatihan klasifikasi akun untuk Tim Perencanaan.
- Pasangan reviu: [[reviu-pengadaan/RP-14-perpanjangan-lisensi-tanggal-awal]] (kesalahan tanggal/perhitungan).

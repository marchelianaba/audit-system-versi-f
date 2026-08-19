<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-pengadaan/AP-27-vendor-lock-in.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AP-27
skill: audit-pengadaan
kategori: PBJ-KONTRAK
severity: HIGH
judul: "Vendor Lock-in pada Infrastruktur Kritis (Tanpa Exit Strategy)"
kriteria_baku: "Perpres 16/2018 Pasal 6 (prinsip) + prinsip persaingan sehat"
tags: [vendor-lock-in, infrastruktur-kritis, exit-strategy, right-to-audit, sufi, audit-pengadaan]
---

# AP-27: Vendor Lock-in pada Infrastruktur Kritis (Tanpa Exit Strategy)

## Pattern Kondisi

Satu vendor menguasai infrastruktur fundamental tanpa alternatif/exit strategy, sehingga negara tergantung penuh. Indikator umum:

- Satu vendor mengontrol topologi/konfigurasi yang tidak dapat di-*handover*
- Pengadaan menggunakan *Surat Perintah Kelanjutan* (bukan tender kompetitif)
- Tidak ada klausul *exit strategy* / *vendor transition* di kontrak
- Tidak ada *right to audit clause* (akses log/metadata bagi auditor)
- Sub-penyedia (PJT) menggantungkan setoran/operasi ke prime tunggal

## Kriteria

Perpres 16/2018 Pasal 6 (prinsip efisien, terbuka, bersaing, adil) + prinsip persaingan sehat — pengadaan infrastruktur kritis tidak boleh menciptakan ketergantungan tunggal tanpa mitigasi.

## Akibat

1. Risiko strategis negara (layanan kritis dikuasai 1 pihak)
2. Harga tidak kompetitif (tidak ada pembanding)
3. Audit teknis terhambat (tanpa *right to audit*)
4. Sulit migrasi/penghentian layanan

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Pemetaan vendor | siapa kontrol infrastruktur kritis |
| Kontrak | klausul exit strategy + right to audit |
| Metode pemilihan | tender vs surat penunjukan/kelanjutan |
| Topologi/arsitektur | dapat di-handover atau terkunci vendor |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AP-27",
  "assigned_to": "{nama anggota}",
  "judul": "Vendor Lock-in {vendor} pada {infrastruktur} Tanpa Exit Strategy",
  "kondisi": "{vendor} menguasai {infrastruktur kritis} ({N} titik) tanpa alternatif. Pengadaan via {surat penunjukan/kelanjutan}, bukan tender. Kontrak tidak memuat klausul exit strategy maupun right to audit; topologi terkunci vendor.",
  "kriteria": "Perpres 16/2018 Pasal 6 + prinsip persaingan sehat — pengadaan infrastruktur kritis tak boleh menciptakan ketergantungan tunggal tanpa mitigasi.",
  "akibat": "Risiko strategis negara; harga tidak kompetitif; audit teknis terhambat; sulit migrasi/penghentian.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **LHA OM TKPPSE 2024** — **PT SUFI** menguasai 187 titik TKPPSE + Metro-E Secure; penunjukan via *Surat Perintah Kelanjutan Pekerjaan* tanpa kompetisi. **LHP Redesain TKPPSE** — Moratel topologi terenkripsi, Lintasarta confidentiality di DC SUFI. Lihat [[lha-om-tkppse-2024]], [[lhp-pengadaan-redesain-tkppse-2026]], [[pattern-temuan]] P-03.

## Catatan

- Rekomendasi: CBA vendor besar vs alternatif sebelum perpanjangan; klausul *right to audit* wajib (lihat [[reviu-pengadaan/RP-13-vendor-confidentiality-audit-trail]]); strategi diversifikasi vendor (min 2 sumber).

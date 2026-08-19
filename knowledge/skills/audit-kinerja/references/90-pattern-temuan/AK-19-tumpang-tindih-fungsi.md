<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/AK-19-tumpang-tindih-fungsi.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AK-19
skill: audit-kinerja
kategori: KINERJA-EFISIENSI
severity: HIGH
judul: "Tumpang Tindih Fungsi Antar-Sistem/Unit (Inefisiensi Anggaran)"
kriteria_baku: "PP 8/2006 prinsip efisiensi + uji 3E SAIPI 2300"
tags: [efisiensi, tumpang-tindih, tkppse, cse, rtbh, duplikasi, audit-kinerja]
---

# AK-19: Tumpang Tindih Fungsi Antar-Sistem/Unit (Inefisiensi Anggaran)

## Pattern Kondisi

Dua atau lebih sistem/unit menjalankan fungsi yang sama atau beririsan, sehingga terjadi duplikasi belanja Operasional & Pemeliharaan (OM) tanpa penambahan nilai. Indikator umum:

- Beberapa sistem dengan fungsi sejenis aktif bersamaan (mis. TKPPSE vs RTBH vs TrustNG vs RPZ)
- Tidak ada *system inventory* terpusat yang memetakan fungsi
- Anggaran OM masing-masing besar tanpa komparasi efektivitas/biaya
- Salah satu sistem dominan terbypass tetap dianggarkan (mis. CNS Rp233,74M vs CSE Rp5,11M)

## Kriteria

PP 8/2006 prinsip **efisiensi** + SAIPI 2300 — sumber daya negara digunakan tanpa duplikasi; audit kinerja menguji apakah output dicapai dengan input minimal.

## Akibat

1. Pemborosan anggaran OM untuk fungsi yang sudah ditangani sistem lain
2. Beban infrastruktur & SDM ganda
3. Aset berisiko *idle* setelah konsolidasi

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Inventarisasi sistem | daftar sistem + fungsi masing-masing |
| RKA/OM tiap sistem | nilai anggaran per sistem |
| Data cakupan/titik | overlap cakupan (mis. 935 titik RTBH = 100% ISP) |
| Kajian efektivitas | komparasi *cost-effectiveness* |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AK-19",
  "assigned_to": "{nama anggota}",
  "judul": "Tumpang Tindih Fungsi {sistem A} dan {sistem B} — Inefisiensi Anggaran OM",
  "kondisi": "{sistem A} (OM Rp{a}) dan {sistem B} (OM Rp{b}) menjalankan fungsi {fungsi} yang beririsan. {sistem B} telah mencakup {X}% cakupan. Tidak ada system inventory + kajian cost-effectiveness yang membandingkan keduanya.",
  "kriteria": "PP 8/2006 prinsip efisiensi + SAIPI 2300 — output harus dicapai tanpa duplikasi sumber daya.",
  "akibat": "Pemborosan anggaran OM duplikatif; beban infrastruktur/SDM ganda; aset berisiko idle pasca-konsolidasi.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **Notisi Tata Kelola Konten Negatif 2025** — **tumpang tindih TKPPSE vs RTBH + TrustNG + RPZ**; CNS (TKPPSE) OM **Rp233,74M** vs CSE-Rugos **Rp5,11M**; RTBH+TrustNG sudah 935 titik (100% ISP). Lihat [[notisi-tata-kelola-konten-negatif-2025]] + [[pattern-temuan]] P-40.

## Catatan

- Rekomendasi: *system inventory* tahunan + komparasi efektivitas/biaya; konsolidasi sistem tumpang tindih.
- Sinergi: AK-17 (efektivitas TKPPSE rendah memperkuat argumen konsolidasi).

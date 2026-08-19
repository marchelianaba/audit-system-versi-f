<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/AK-17-sistem-pengendalian-bypass.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AK-17
skill: audit-kinerja
kategori: KINERJA-EFEKTIVITAS
severity: CRITICAL
judul: "Sistem/Teknologi Pengendalian Dapat Di-bypass (Efektivitas Rendah)"
kriteria_baku: "PP 8/2006 tentang Pelaporan Keuangan dan Kinerja Instansi Pemerintah + SAIPI 2200; uji 3E"
tags: [efektivitas, tkppse, teknologi-usang, bypass, audit-kinerja, 3e]
---

# AK-17: Sistem/Teknologi Pengendalian Dapat Di-bypass (Efektivitas Rendah)

## Pattern Kondisi

Sistem/teknologi yang dibangun untuk fungsi pengendalian ternyata dapat dilewati (*bypass*) oleh perkembangan teknologi, sehingga efektivitasnya jauh di bawah ekspektasi. Indikator umum:

- Hasil uji laboratorium/sampling menunjukkan tingkat keberhasilan rendah (mis. 0/40 akses berhasil diblok)
- Teknologi inti sudah *End-of-Life* / lisensi kedaluwarsa (mis. Oracle Linux 7 EOL)
- Metode pengendalian dapat dilewati protokol modern (HTTPS, DoH, DoT, QUIC, VPN)
- Efektivitas terukur jauh di bawah alternatif (mis. 22,44% vs 79,60% / 81,45%)
- Aset/belanja modal besar berisiko *idle* bila sistem dihentikan

## Kriteria

PP 8/2006 + SAIPI Standar 2200 (Perencanaan Penugasan) & 2300 (Pelaksanaan) mensyaratkan audit kinerja menguji **3E**:

> Efektif (tujuan/outcome tercapai), Efisien (rasio output-input optimal), Ekonomis (biaya perolehan input hemat).

Sistem dinilai **tidak efektif** bila tujuan pengendalian tidak tercapai pada tingkat yang memadai dibanding kriteria/benchmark.

## Akibat

1. Tujuan kebijakan (mis. pemblokiran konten ilegal) tidak tercapai
2. Belanja modal/aset menjadi berisiko *idle* (mis. aset BMN Rp1,59 triliun)
3. Temuan berulang BPK + risiko reputasi
4. Anggaran OM berlanjut untuk sistem yang tidak efektif (pemborosan)

## Bukti Yang Harus Dicari

| Dokumen | Section / Field | Yang dicari |
|---------|-----------------|-------------|
| Hasil uji lab/sampling | tabel pengujian | *success-rate* pemblokiran/pengendalian |
| Spesifikasi teknis & lisensi | versi + masa berlaku | versi teknologi + tanggal EOL |
| Benchmark sistem sejenis | komparasi efektivitas | pembanding (mis. RTBH/RPZ) |
| Roadmap redesain | rencana + milestone | ada/tidak rencana upgrade |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AK-17",
  "assigned_to": "{nama anggota}",
  "judul": "Efektivitas {sistem} Hanya {X}% — Dapat Di-bypass Teknologi Modern",
  "kondisi": "Pengujian atas {sistem} TA {YYYY} menunjukkan efektivitas {X}% (vs pembanding {Y}%). Uji laboratorium {a}/{b} akses berhasil dikendalikan. Teknologi inti {versi} EOL {tgl}; dapat dilewati {HTTPS/DoH/DoT/QUIC/VPN}. Nilai aset/belanja terkait Rp{Z}.",
  "kriteria": "PP 8/2006 + SAIPI 2200/2300 — audit kinerja menguji 3E; sistem harus efektif mencapai tujuan pengendalian.",
  "akibat": "Tujuan kebijakan tidak tercapai; aset berisiko idle; OM berlanjut untuk sistem tidak efektif (pemborosan).",
  "dokumen_sumber": [
    {"file": "...", "halaman": "X", "kutipan": "hasil uji 0/40 ..."}
  ]
}
```

## Contoh Kasus Historis

- **LHP Kinerja BPK PSTE (14/LHP/XVI/02/2025)** — TKPPSE efektivitas **22,44%** vs RPZ 79,60% & RTBH 81,45%; uji lab **0/40** akses murni TKPPSE; Oracle Linux 7 EOL 31 Des 2024; aset BMN TKPPSE Rp1,59T berisiko idle. Lihat [[pattern-temuan]] P-29 + [[bpk-laporan-hasil-pemeriksaan]].

## Catatan

- Rekomendasi standar: *sunset policy* untuk teknologi efektivitas <50%; redesain dengan **milestone** (bukan kajian tanpa eksekusi → lihat [[pemantauan-pengadaan/PMP-56-kajian-tanpa-milestone]]).
- Sinergi: AK-19 (tumpang tindih), [[reviu-pengadaan/RP-12-kajian-tanpa-rencana-aksi]].

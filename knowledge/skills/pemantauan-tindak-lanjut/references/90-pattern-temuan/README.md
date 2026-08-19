<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/pemantauan-tindak-lanjut/README.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

# Pattern Temuan — Pemantauan Tindak Lanjut

Index pattern temuan yang berlaku untuk skill `pemantauan-tindak-lanjut`. Tambahkan pattern baru di folder ini, lalu update tabel di bawah.

## Index

| ID | Judul | Kategori | Severity | Kriteria Baku |
|----|-------|----------|----------|---------------|
| PTL-48 | Rekomendasi Struktural Outstanding >2 Tahun (Butuh Regulasi/MoU) | TLHP-STRUKTURAL | HIGH | UU 15/2004 Pasal 20 + Pedoman Pemantauan TLHP |
| PTL-49 | Asimetri TL Eksternal vs Internal Antar-Ditjen | TLHP-KINERJA | MEDIUM | Pedoman Pemantauan TLHP |
| PTL-50 | Verifikasi Outstanding Finansial Belum Tuntas (Scope Gap) | TLHP-FINANSIAL | HIGH | Mandat BPK + SAIPI 2300 |
| PTL-51 | Ownership Rekomendasi Fragmen Pasca-Likuidasi/SOTK | TLHP-OWNERSHIP | HIGH | Perpres/Pedoman TLHP + SOTK |
| PTL-52 | Outstanding Finansial Belum Disetor ke Kas Negara | TLHP-FINANSIAL | HIGH | UU 15/2004 + tindak lanjut rekomendasi |

## Kategori yang dipakai

- `TLHP-STRUKTURAL` — rekomendasi yang butuh regulasi/MoU (bukan aksi internal)
- `TLHP-KINERJA` — kinerja penyelesaian TL (rate, asimetri antar-unit)
- `TLHP-FINANSIAL` — outstanding finansial (setor kas negara, verifikasi)
- `TLHP-OWNERSHIP` — kepemilikan rekomendasi pasca-SOTK/likuidasi

## Sumber data pattern

Pattern di folder ini disusun dari pemantauan TLHP Inspektorat II TA 2025–2026:

- TLHP eksternal Simwas IR2 (Rp200,89M outstanding; JAR Rp171,59M)
- TLHP internal Simwas IR2 (Rp30,27M; warisan Aptaka JAR + HUB.ID)
- TLRHP BPK Semester II 2025 (1.960 rek, 82,7% sesuai, 71 belum)
- Pemantauan TLHP Ekdig/Wasdig November 2025 (Wasdig 17,07% vs Ekdig 83,33%)

Setiap pattern wajib menyebut kasus historis di section "Contoh Kasus Historis".

## Lihat juga

- [[pattern-temuan]] — katalog induk (P-24, P-25, P-26, P-27)
- [[tlhp-eksternal-simwas-ir2]] / [[tlhp-internal-simwas-ir2]] / [[tlrhp-bpk-semester-2-2025]]
- [[audit-pengadaan/README]] — temuan asal (OM TKPPSE, JAR, BTS 4G)

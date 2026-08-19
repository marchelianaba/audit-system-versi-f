<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/evaluasi-sakip/ESK-34-hasil-pengukuran-belum-decision-tool.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: ESK-34
skill: evaluasi-sakip
kategori: SAKIP-PEMANFAATAN
severity: MEDIUM
judul: "Hasil Pengukuran Belum Dipakai sebagai Decision Tool"
kriteria_baku: "Permenpan-RB 88/2021 (pemanfaatan hasil evaluasi kinerja)"
tags: [sakip, pemanfaatan, decision-tool, reward-punishment, monev, permenpanrb-88]
---

# ESK-34: Hasil Pengukuran Belum Dipakai sebagai Decision Tool

## Pattern Kondisi

Hasil pengukuran kinerja tersedia tetapi belum dimanfaatkan sebagai dasar pengambilan keputusan manajemen. Indikator umum:

- Hasil pengukuran tidak jadi dasar reward/punishment
- Tidak ada perubahan strategi/alokasi berbasis hasil kinerja
- Pengembangan kompetensi tidak dikaitkan dengan capaian
- Rekomendasi monev berkala belum cukup mendorong pencapaian

## Kriteria

Permenpan-RB 88/2021 — hasil evaluasi & pengukuran kinerja wajib dimanfaatkan untuk perbaikan kinerja (perubahan strategi, reward/punishment, pengembangan kompetensi).

## Akibat

1. Siklus PDCA kinerja terputus (ukur tapi tidak dipakai)
2. Tidak ada insentif perbaikan kinerja
3. Stagnasi nilai AKIP (lihat ESK-30)

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Notula rapim/keputusan | apakah merujuk data kinerja |
| Kebijakan reward/punishment | dikaitkan dengan capaian? |
| Rencana pengembangan kompetensi | berbasis gap kinerja? |
| Rekomendasi monev berkala | ditindaklanjuti? |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-ESK-34",
  "assigned_to": "{nama anggota}",
  "judul": "Hasil Pengukuran Kinerja {satker} Belum Dipakai sebagai Decision Tool",
  "kondisi": "Hasil pengukuran kinerja {satker} TA {YYYY} tersedia, namun belum dimanfaatkan untuk: (a) reward/punishment; (b) perubahan strategi/alokasi; (c) pengembangan kompetensi. Rekomendasi monev berkala belum cukup mendorong pencapaian.",
  "kriteria": "Permenpan-RB 88/2021 — hasil evaluasi & pengukuran wajib dimanfaatkan untuk perbaikan kinerja.",
  "akibat": "Siklus PDCA terputus; tidak ada insentif perbaikan; stagnasi nilai AKIP.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **ND-133 Atensi SAKIP** — "Hasil pengukuran kinerja belum dimanfaatkan sebagai dasar pengambilan keputusan seperti perubahan strategi, reward/punishment, dan pengembangan kompetensi". Lihat [[nota-dinas-ir2-mei-2026]] (ND-133).

## Catatan

- Rekomendasi: jadikan aplikasi janji kinerja & SKP sebagai *decision tool*.
- Sinergi: ESK-31 (pengukuran administratif), [[audit-kinerja/AK-21-capaian-tidak-traceable]].

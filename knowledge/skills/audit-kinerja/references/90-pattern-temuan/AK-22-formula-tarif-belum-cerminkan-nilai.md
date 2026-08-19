<!-- ============================================================
     DIINJEKSI OTOMATIS dari wiki — SNAPSHOT BEKU (turunan FREE)
     Sumber  : knowledge/wiki/temuan-patterns/audit-kinerja/AK-22-formula-tarif-belum-cerminkan-nilai.md
     JANGAN diedit manual. Untuk menyegarkan, jalankan ulang:
       python scripts/inject_wiki_to_skills.py --apply
     ============================================================ -->

---
id: AK-22
skill: audit-kinerja
kategori: KINERJA-DESAIN
severity: MEDIUM
judul: "Formula Tarif/Indikator Belum Mencerminkan Nilai Ekonomi/Outcome"
kriteria_baku: "PP 8/2006 + pedoman penyusunan formula tarif/PNBP + uji 3E"
tags: [formula, tarif, ipfr, bhp, desain-indikator, outcome, audit-kinerja]
---

# AK-22: Formula Tarif/Indikator Belum Mencerminkan Nilai Ekonomi/Outcome

## Pattern Kondisi

Formula tarif (mis. BHP/IPFR) atau indikator kinerja belum mencerminkan nilai ekonomi pemanfaatan sumber daya atau outcome yang sebenarnya. Indikator umum:

- Variabel formula (mis. N, K, C pada IPFR) belum relevan dengan kondisi industri terkini
- Peraturan turunan (insentif, optimalisasi) belum ada
- Indikator mengukur proses/realisasi, bukan outcome/nilai ekonomi
- Pedoman teknis + pembagian tanggung jawab antar-Ditjen belum jelas pasca-SOTK

## Kriteria

PP 8/2006 + pedoman penyusunan formula tarif/PNBP + uji 3E — desain tarif/indikator harus mencerminkan nilai ekonomi dan mendorong outcome yang diharapkan.

## Akibat

1. Penerimaan negara tidak optimal / tidak adil
2. Insentif yang salah (tidak mendorong efisiensi spektrum/sumber daya)
3. Sengketa dengan wajib bayar atas dasar perhitungan
4. Risiko temuan BPK berulang

## Bukti Yang Harus Dicari

| Dokumen | Yang dicari |
|---------|-------------|
| Formula tarif (PP/Permen) | variabel + dasar perhitungan |
| Kajian nilai ekonomi | relevansi variabel dgn industri |
| Peraturan turunan | insentif/optimalisasi ada/tidak |
| Pembagian tugas antar-Ditjen | kejelasan pasca-SOTK |

## Format Temuan (untuk diisi agen ke `append_temuan`)

```json
{
  "sasaran_id": "S-AK-22",
  "assigned_to": "{nama anggota}",
  "judul": "Formula {tarif/indikator} Belum Mencerminkan Nilai Ekonomi/Outcome",
  "kondisi": "Formula {nama} TA {YYYY}: variabel {N/K/C} belum relevan dengan {kondisi industri}; peraturan turunan {insentif/optimalisasi} belum ada; pembagian tanggung jawab antar-Ditjen belum jelas pasca-SOTK.",
  "kriteria": "PP 8/2006 + pedoman penyusunan formula + uji 3E — desain tarif/indikator harus mencerminkan nilai ekonomi & mendorong outcome.",
  "akibat": "Penerimaan negara tidak optimal; insentif salah; sengketa wajib bayar; temuan BPK berulang.",
  "dokumen_sumber": [{"file": "...", "halaman": "X", "kutipan": "..."}]
}
```

## Contoh Kasus Historis

- **LHP Kinerja BPK IPFR-ISR (17/T/LHP/DJPKN-III/PPN.02/01/2026)** — formula BHP IPFR belum mencerminkan nilai ekonomi pita frekuensi; pedoman optimalisasi SFR + kewajiban pembangunan belum memadai; risiko tumpang tindih antar-Ditjen; *harmful interference* 900 MHz kereta cepat. Lihat [[bpk-kinerja-ipfr-isr-2026]].

## Catatan

- Terkait erat dengan rezim PNBP — lihat [[pnbp-bhp-telekomunikasi]].
- Rekomendasi: kaji ulang variabel formula berbasis nilai ekonomi; terbitkan peraturan turunan + pedoman optimalisasi.

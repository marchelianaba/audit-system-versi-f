#!/usr/bin/env python3
"""
extract_lke.py — Ekstrak struktur LKE SAKIP ke JSON terstruktur
Penggunaan: python extract_lke.py <path_lke_file.xls> [output.json]

Struktur kolom aktual LKE Komdigi:
  KOMPONEN  : C0=kode(1.0), C1=nama, C4=bobot, C9=nilai_mandiri, C16=nilai_apip
              C19=catatan_evaluator, C20=rekomendasi_evaluator
  SUB-KOMP  : C1=kode(1.a), C2=nama, C4=bobot, C7=predikat_mandiri,
              C14=predikat_apip, C16=nilai_akhir_apip
  KRITERIA  : C2=nomor(1)), C3=deskripsi, C5=jawaban_mandiri, C6=nilai_mandiri,
              C12=predikat_apip, C13=nilai_apip, C18=keterangan_apip,
              C19=contoh_bukti, C20=url_bukti (dengan nama file dalam kurung)
"""
import sys
import json
import re
import xlrd

def clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    s = re.sub(r'\n+', '\n', s)
    return s

def extract_urls(url_cell_text):
    """
    Ekstrak URL dari sel yang berisi URL + nama file dalam kurung.
    Contoh: 'https://evsakip.../pdf123.pdf (nama_file.pdf)'
    Atau beberapa URL dipisah newline.
    """
    if not url_cell_text:
        return []
    urls = []
    # Ambil semua pola URL
    found = re.findall(r'https?://[^\s\(\)]+', url_cell_text)
    for u in found:
        u = u.rstrip('.,;')
        if u not in urls:
            urls.append(u)
    return urls

def detect_row_type(row_vals):
    """
    Tentukan tipe baris berdasarkan pola kode di kolom yang tepat.
    - komponen    : C0 = '1.0', '2.0', '3.0', '4.0'
    - sub_komponen: C1 = '1.a', '1.b', '2.a', dst. (C0 kosong)
    - kriteria    : C2 = '1)', '2)', '10)', dst. (C0 dan C1 kosong)
    """
    c0 = clean(row_vals[0]) if len(row_vals) > 0 else ""
    c1 = clean(row_vals[1]) if len(row_vals) > 1 else ""
    c2 = clean(row_vals[2]) if len(row_vals) > 2 else ""

    if re.match(r'^[1-4]\.0$', c0):
        return 'komponen'
    if re.match(r'^[1-4]\.[a-z]$', c1) and not c0:
        return 'sub_komponen'
    if re.match(r'^\d+\)$', c2) and not c0 and not re.match(r'^[1-4]\.[a-z]$', c1):
        return 'kriteria'
    return 'skip'

def safe_float(v):
    try:
        s = str(v).replace('%', '').strip()
        return float(s) if s else None
    except:
        return None

def extract_lke(filepath):
    wb = xlrd.open_workbook(filepath)
    s = wb.sheet_by_index(0)

    result = {
        "metadata": {
            "unit_kerja": "",
            "tahun": "",
            "sumber_file": filepath,
        },
        "nilai_total": {
            "mandiri": None,
            "apip": None,
        },
        "komponen": []
    }

    # Metadata dari baris 0-4
    for r in range(5):
        v = clean(s.cell(r, 0).value)
        if any(k in v.upper() for k in ['DIREKTORAT', 'BADAN', 'KEMENTERIAN', 'SETJEN', 'ITJEN']):
            result["metadata"]["unit_kerja"] = v
        m = re.search(r'(20\d\d)', v)
        if m:
            result["metadata"]["tahun"] = m.group(1)

    # Baris 8: nilai total keseluruhan
    if s.nrows > 8:
        r8 = [s.cell(8, c).value for c in range(s.ncols)]
        # C9=nilai_mandiri, C16=nilai_apip
        result["nilai_total"]["mandiri"] = safe_float(r8[9]) if len(r8) > 9 else None
        result["nilai_total"]["apip"] = safe_float(r8[16]) if len(r8) > 16 else None

    current_komponen = None
    current_sub_komponen = None

    for row in range(9, s.nrows):
        row_vals = [s.cell(row, c).value for c in range(s.ncols)]
        row_type = detect_row_type(row_vals)

        if row_type == 'skip':
            continue

        if row_type == 'komponen':
            # C0=kode, C1=nama, C4=bobot
            # C9=nilai_mandiri, C10=%mandiri
            # C16=nilai_apip,   C17=%apip
            # C19=catatan_evaluator, C20=rekomendasi_evaluator
            current_komponen = {
                "kode": clean(row_vals[0]),
                "nama": clean(row_vals[1]),
                "bobot": safe_float(row_vals[4]) if len(row_vals) > 4 else None,
                "penilaian_mandiri": {
                    "nilai": safe_float(row_vals[9]) if len(row_vals) > 9 else None,
                    "persen": safe_float(row_vals[10]) if len(row_vals) > 10 else None,
                },
                "penilaian_apip": {
                    "nilai": safe_float(row_vals[16]) if len(row_vals) > 16 else None,
                    "persen": safe_float(row_vals[17]) if len(row_vals) > 17 else None,
                },
                "catatan_evaluator": clean(row_vals[19]) if len(row_vals) > 19 else "",
                "rekomendasi_evaluator": clean(row_vals[20]) if len(row_vals) > 20 else "",
                "sub_komponen": []
            }
            result["komponen"].append(current_komponen)
            current_sub_komponen = None

        elif row_type == 'sub_komponen' and current_komponen is not None:
            # C1=kode, C2=nama, C4=bobot
            # Mandiri: C5=%terpenuhi, C6=nilai, C7=predikat, C9=nilai_akhir, C10=%
            # APIP:    C12=%terpenuhi, C13=nilai, C14=predikat, C16=nilai_akhir, C17=%
            current_sub_komponen = {
                "kode": clean(row_vals[1]),
                "nama": clean(row_vals[2]),
                "bobot": safe_float(row_vals[4]) if len(row_vals) > 4 else None,
                "penilaian_mandiri": {
                    "persen_terpenuhi": safe_float(row_vals[5]) if len(row_vals) > 5 else None,
                    "nilai": safe_float(row_vals[6]) if len(row_vals) > 6 else None,
                    "predikat": clean(row_vals[7]) if len(row_vals) > 7 else "",
                    "nilai_akhir": safe_float(row_vals[9]) if len(row_vals) > 9 else None,
                },
                "penilaian_apip": {
                    "persen_terpenuhi": safe_float(row_vals[12]) if len(row_vals) > 12 else None,
                    "nilai": safe_float(row_vals[13]) if len(row_vals) > 13 else None,
                    "predikat": clean(row_vals[14]) if len(row_vals) > 14 else "",
                    "nilai_akhir": safe_float(row_vals[16]) if len(row_vals) > 16 else None,
                },
                "kriteria": []
            }
            current_komponen["sub_komponen"].append(current_sub_komponen)

        elif row_type == 'kriteria' and current_sub_komponen is not None:
            # C2=nomor, C3=deskripsi
            # Mandiri: C5=jawaban, C6=nilai_mandiri
            # APIP:    C12=predikat, C13=nilai, C18=keterangan (Sesuai/catatan)
            # C19=contoh_bukti_dukung, C20=URL bukti dukung upload
            nomor = clean(row_vals[2])
            deskripsi = clean(row_vals[3]) if len(row_vals) > 3 else ""
            jawaban_mandiri = clean(row_vals[5]) if len(row_vals) > 5 else ""
            nilai_mandiri = safe_float(row_vals[6]) if len(row_vals) > 6 else None
            predikat_apip = clean(row_vals[12]) if len(row_vals) > 12 else ""
            nilai_apip = safe_float(row_vals[13]) if len(row_vals) > 13 else None
            keterangan_apip = clean(row_vals[18]) if len(row_vals) > 18 else ""
            contoh_bukti = clean(row_vals[19]) if len(row_vals) > 19 else ""
            url_raw = clean(row_vals[20]) if len(row_vals) > 20 else ""
            urls = extract_urls(url_raw)

            kriteria = {
                "nomor": nomor,
                "deskripsi": deskripsi,
                "penilaian_mandiri": {
                    "jawaban": jawaban_mandiri,
                    "nilai": nilai_mandiri,
                },
                "penilaian_apip_existing": {
                    "predikat": predikat_apip,
                    "nilai": nilai_apip,
                    "keterangan": keterangan_apip,
                },
                # Field kosong untuk diisi evaluator baru:
                "penilaian_apip_baru": {
                    "jawaban": "",        # Ya/Tidak
                    "predikat": "",       # A/BB/B/CC/C/D/E
                    "nilai": None,
                    "keterangan": "",     # hasil analisis dokumen
                },
                "catatan_evaluator": "",  # temuan/catatan
                "rekomendasi_evaluator": "",
                "contoh_bukti_dukung": contoh_bukti,
                "url_bukti_dukung": urls,
                "analisis_dokumen": []    # diisi saat fetch URL
            }
            current_sub_komponen["kriteria"].append(kriteria)

    return result

def print_summary(data):
    print(f"Unit Kerja   : {data['metadata']['unit_kerja']}")
    print(f"Tahun        : {data['metadata']['tahun']}")
    print(f"Nilai Mandiri: {data['nilai_total']['mandiri']}")
    print(f"Nilai APIP   : {data['nilai_total']['apip']}")
    print(f"Komponen     : {len(data['komponen'])}")

    total_sk = 0
    total_kr = 0
    total_url = 0

    for k in data['komponen']:
        sk_count = len(k['sub_komponen'])
        total_sk += sk_count
        for sk in k['sub_komponen']:
            kr_count = len(sk['kriteria'])
            total_kr += kr_count
            for kr in sk['kriteria']:
                total_url += len(kr['url_bukti_dukung'])
            print(f"  {k['kode']} {k['nama'][:30]:30s} | "
                  f"{sk['kode']} {sk['nama'][:30]:30s} | "
                  f"{kr_count} kriteria")

    print(f"\nTotal sub-komponen : {total_sk}")
    print(f"Total kriteria     : {total_kr}")
    print(f"Total URL bukti    : {total_url}")

def main():
    if len(sys.argv) < 2:
        print("Penggunaan: python extract_lke.py <file.xls> [output.json]")
        sys.exit(1)

    filepath = sys.argv[1]
    output_path = (sys.argv[2] if len(sys.argv) > 2
                   else filepath.replace('.xls', '_extracted.json').replace('.xlsx', '_extracted.json'))

    print(f"Membaca: {filepath}\n")
    data = extract_lke(filepath)
    print_summary(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\nOutput: {output_path}")


if __name__ == "__main__":
    main()

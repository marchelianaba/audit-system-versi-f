#\!/usr/bin/env python3
"""
download_bukti.py — Download semua bukti dukung dari LKE ke folder lokal
Jalankan langsung di komputer (bukan di Claude sandbox):

  python download_bukti.py <lke_extracted.json> [folder_output]

Contoh:
  python download_bukti.py "_KKP/lke_extracted.json"
  python download_bukti.py "_KKP/lke_extracted.json" "_KKP/bukti_dukung"

Setelah selesai, jalankan di Claude:
  python read_local_bukti.py lke_extracted.json bukti_dukung/

Butuh: pip install requests
"""
import json
import os
import re
import sys
import time
import zipfile

try:
    import requests
except ImportError:
    print("ERROR: install dulu dengan: pip install requests")
    sys.exit(1)

# ── HELPER ────────────────────────────────────────────────────────────────────
def safe_name(s, maxlen=60):
    """Nama file/folder yang aman untuk semua OS."""
    s = re.sub(r'[\\/:*?"<>|]', '_', s)
    return s[:maxlen].rstrip('. ')

def sk_folder(kode):
    """'1.a' → '1_a' (aman di Windows & Linux)."""
    return kode.replace('.', '_')

def get_ext(url):
    """Ambil ekstensi dari URL."""
    m = re.search(r'\.(pdf|xlsx|xls|zip|docx|jpg|jpeg|png)(?:[?#]|$)', url, re.I)
    return ('.' + m.group(1).lower()) if m else '.bin'

def extract_zip(zip_path, dest_folder):
    """Ekstrak ZIP ke subfolder."""
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(dest_folder)
        return True
    except Exception as e:
        print(f"    [\!] Gagal ekstrak ZIP: {e}")
        return False

# ── DOWNLOAD ──────────────────────────────────────────────────────────────────
def download_bukti(json_path, output_folder=None):
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)

    base = output_folder or os.path.join(os.path.dirname(os.path.abspath(json_path)), 'bukti_dukung')
    os.makedirs(base, exist_ok=True)
    print(f"Output folder: {base}\n")

    log  = []
    total = ok = skip = fail = 0

    session = requests.Session()
    session.headers['User-Agent'] = (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 Chrome/120.0 Safari/537.36'
    )

    for k in data['komponen']:
        print(f"\n{'='*60}")
        print(f"  {k['kode']} {k['nama']}")
        print(f"{'='*60}")

        for sk in k['sub_komponen']:
            sk_dir = os.path.join(base, sk_folder(sk['kode']))
            os.makedirs(sk_dir, exist_ok=True)

            for kr in sk['kriteria']:
                nomor = kr['nomor'].rstrip(')').strip()
                kr_dir = os.path.join(sk_dir, f"kr{nomor}")
                os.makedirs(kr_dir, exist_ok=True)

                urls = kr.get('url_bukti_dukung', [])
                if not urls:
                    continue

                print(f"\n  {sk['kode']}/kr{nomor}  {kr['deskripsi'][:55]}...")

                for idx, url in enumerate(urls, 1):
                    total += 1
                    ext   = get_ext(url)
                    fname = f"{idx:02d}{ext}"
                    fpath = os.path.join(kr_dir, fname)

                    # Skip jika sudah ada dan tidak kosong
                    if os.path.exists(fpath) and os.path.getsize(fpath) > 500:
                        skip += 1
                        print(f"    [{idx:02d}] SKIP  {fname} (sudah ada)")
                        continue

                    try:
                        r = session.get(url, timeout=30, stream=True)
                        if r.status_code == 200:
                            with open(fpath, 'wb') as f_out:
                                for chunk in r.iter_content(8192):
                                    f_out.write(chunk)
                            size_kb = os.path.getsize(fpath) / 1024

                            # Ekstrak ZIP otomatis
                            if ext == '.zip' and size_kb > 0:
                                zip_dir = fpath.replace('.zip', '_extracted')
                                if extract_zip(fpath, zip_dir):
                                    fname += f" → extracted"

                            ok += 1
                            print(f"    [{idx:02d}] OK    {fname} ({size_kb:.0f} KB)")
                            log.append({'status': 'ok', 'url': url, 'path': fpath})
                        else:
                            fail += 1
                            print(f"    [{idx:02d}] HTTP  {r.status_code} — {url[-60:]}")
                            log.append({'status': f'http_{r.status_code}', 'url': url})

                    except requests.Timeout:
                        fail += 1
                        print(f"    [{idx:02d}] TIMEOUT — {url[-60:]}")
                        log.append({'status': 'timeout', 'url': url})
                    except Exception as e:
                        fail += 1
                        print(f"    [{idx:02d}] ERROR  {e}")
                        log.append({'status': 'error', 'url': url, 'error': str(e)})

                    time.sleep(0.25)  # hormat ke server

    # Ringkasan
    print(f"\n{'='*60}")
    print(f"  SELESAI")
    print(f"  Total URL   : {total}")
    print(f"  Berhasil    : {ok}")
    print(f"  Dilewati    : {skip}  (sudah ada)")
    print(f"  Gagal       : {fail}")
    print(f"  Disimpan di : {base}")
    print(f"{'='*60}")

    log_path = os.path.join(base, '_download_log.json')
    with open(log_path, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"\n  Log: {log_path}")

    if fail > 0:
        print(f"\n  [\!] {fail} file gagal. Jalankan ulang script untuk retry.")

    print("\n  Langkah berikutnya (di Claude):")
    print("  python read_local_bukti.py lke_extracted.json bukti_dukung/")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    download_bukti(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)

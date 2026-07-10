#!/usr/bin/env python3
"""Susun ulang daftar "Sorotan Redaksi" di index.html menjadi "Terpopuler"
berdasarkan data kunjungan nyata dari GoatCounter (7 hari terakhir).

Token API dibaca dari env GOAT_TOKEN atau ~/.config/warta-kini/goatcounter-token.
Tanpa token / tanpa data memadai, script tidak mengubah apa pun (no-op) —
peringkat pilihan redaksi tetap dipakai.
"""
import datetime
import json
import os
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = 'https://warta-kini.goatcounter.com'
MIN_ARTIKEL = 3


def token() -> str | None:
    if os.environ.get('GOAT_TOKEN'):
        return os.environ['GOAT_TOKEN']
    f = pathlib.Path.home() / '.config' / 'warta-kini' / 'goatcounter-token'
    return f.read_text().strip() if f.exists() else None


tok = token()
if not tok:
    print('terpopuler: token GoatCounter tidak ada — dilewati (Sorotan Redaksi tetap).')
    sys.exit(0)

mulai = (datetime.date.today() - datetime.timedelta(days=7)).isoformat()
req = urllib.request.Request(
    f'{SITE}/api/v0/stats/hits?start={mulai}&limit=20',
    headers={'Authorization': f'Bearer {tok}', 'Content-Type': 'application/json'},
)
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
except Exception as e:  # noqa: BLE001 — kegagalan analitik tak boleh menggagalkan edisi
    print(f'terpopuler: gagal mengambil data GoatCounter ({e}) — dilewati.')
    sys.exit(0)

# path populer → jumlah kunjungan
hitung: dict[str, int] = {}
for hit in data.get('hits', []):
    m = re.search(r'artikel/([a-z0-9-]+\.html)', hit.get('path', ''))
    if m:
        hitung[m.group(1)] = hitung.get(m.group(1), 0) + int(hit.get('count', 0))

peringkat = sorted(hitung, key=hitung.get, reverse=True)[:5]
if len(peringkat) < MIN_ARTIKEL:
    print(f'terpopuler: data belum cukup ({len(peringkat)} artikel) — dilewati.')
    sys.exit(0)

idx = ROOT / 'index.html'
html = idx.read_text()

# judul tiap artikel diambil dari h1 halaman artikelnya
items = []
for fname in peringkat:
    p = ROOT / 'artikel' / fname
    if not p.exists():
        continue
    m = re.search(r'<h1>(.*?)</h1>', p.read_text(), re.S)
    judul = re.sub(r'\s+', ' ', m.group(1)).strip() if m else fname
    items.append(f'          <li><a href="artikel/{fname}">{judul}</a></li>')

if len(items) < MIN_ARTIKEL:
    print('terpopuler: artikel populer tidak cocok dengan edisi berjalan — dilewati.')
    sys.exit(0)

blok_baru = ('<h2 class="section-title">Terpopuler</h2>\n        <ol>\n'
             + '\n'.join(items) + '\n        </ol>')
html, n = re.subn(
    r'<h2 class="section-title">(?:Sorotan Redaksi|Terpopuler)</h2>\s*<ol>.*?</ol>',
    blok_baru, html, count=1, flags=re.S)
if n:
    idx.write_text(html)
    print(f'terpopuler: peringkat diperbarui dari data kunjungan ({len(items)} artikel).')
else:
    print('terpopuler: blok peringkat tidak ditemukan di index.html — dilewati.')

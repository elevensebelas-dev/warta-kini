#!/usr/bin/env python3
"""Bangun indeks.json — indeks pencarian seluruh artikel lintas edisi.

Memindai edisi berjalan (artikel/) dan semua snapshot di arsip/, lalu
menulis indeks ringkas yang dibaca cari.html di sisi peramban.
"""
import html as htmllib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
BULAN = {b: i for i, b in enumerate(
    ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
     'Agustus', 'September', 'Oktober', 'November', 'Desember'])}


def teks(fragmen: str) -> str:
    return re.sub(r'\s+', ' ', htmllib.unescape(
        re.sub(r'<[^>]+>', ' ', fragmen))).strip()


def tanggal_dari_topbar(html: str) -> str:
    """'Jumat, 10 Juli 2026' → '2026-07-10'."""
    m = re.search(r'<strong>[A-Za-z]+,\s*(\d{1,2})\s+(\w+)\s+(\d{4})</strong>', html)
    if m and (bln := BULAN.get(m.group(2))):
        return f'{m.group(3)}-{bln:02d}-{int(m.group(1)):02d}'
    return ''


def rekam(p: pathlib.Path, url: str, edisi: str) -> dict | None:
    html = p.read_text()
    m_judul = re.search(r'<h1>(.*?)</h1>', html, re.S)
    if not m_judul:
        return None

    rubrik, kanal = '', ''
    if m := re.search(r'<p class="kicker kanal-([a-z]+)">(.*?)</p>', html, re.S):
        kanal = m.group(1)
        rubrik = teks(m.group(2)).split('·')[0].strip()
    elif m := re.search(r'<p class="kicker">(.*?)</p>', html, re.S):
        # Snapshot lama: belum memakai kelas kanal berwarna
        rubrik = teks(m.group(1)).split('·')[0].strip()
        kanal = rubrik.lower()

    standfirst = ''
    if m := re.search(r'<p class="standfirst">(.*?)</p>', html, re.S):
        standfirst = teks(m.group(1))

    tags = []
    if m := re.search(r'<div class="article-tags">(.*?)</div>', html, re.S):
        tags = [teks(t) for t in re.findall(r'<span>(.*?)</span>', m.group(1), re.S)]

    return {
        'judul': teks(m_judul.group(1)),
        'ringkas': standfirst,
        'rubrik': rubrik or 'Lainnya',
        'kanal': kanal,
        'tag': tags,
        'url': url,
        'edisi': edisi or tanggal_dari_topbar(html),
    }


def main() -> None:
    data: list[dict] = []

    # Edisi berjalan
    edisi_kini = tanggal_dari_topbar((ROOT / 'index.html').read_text())
    for p in sorted((ROOT / 'artikel').glob('*.html')):
        if r := rekam(p, f'artikel/{p.name}', edisi_kini):
            r['terbaru'] = True
            data.append(r)

    # Snapshot arsip
    arsip = ROOT / 'arsip'
    if arsip.is_dir():
        for folder in sorted((d for d in arsip.iterdir()
                              if d.is_dir() and re.fullmatch(r'\d{4}-\d{2}-\d{2}', d.name)),
                             reverse=True):
            for p in sorted((folder / 'artikel').glob('*.html')):
                if r := rekam(p, f'arsip/{folder.name}/artikel/{p.name}', folder.name):
                    r['terbaru'] = False
                    data.append(r)

    data.sort(key=lambda r: (r['edisi'], r['judul']), reverse=True)
    (ROOT / 'indeks.json').write_text(
        json.dumps({'dibuat': edisi_kini, 'jumlah': len(data), 'artikel': data},
                   ensure_ascii=False, separators=(',', ':')))
    edisi = len({r['edisi'] for r in data})
    print(f'indeks: {len(data)} artikel dari {edisi} edisi.')


if __name__ == '__main__':
    main()

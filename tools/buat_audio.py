#!/usr/bin/env python3
"""Bangun audio artikel (text-to-speech) dan sisipkan pemutarnya.

Memakai suara Indonesia bawaan macOS (Damayanti) via `say` — sepenuhnya
offline, tanpa layanan pihak ketiga — lalu dikonversi ke MP3 dengan ffmpeg.

Dipanggil oleh update.sh setiap edisi baru. Artikel yang teksnya tidak
berubah dilewati (hash disimpan di audio/.hash.json).
"""
import hashlib
import html as htmllib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
ARTIKEL = ROOT / 'artikel'
AUDIO = ROOT / 'audio'
SUARA = 'Damayanti'
BITRATE = '24k'

PLAYER_RE = re.compile(r'\n?\s*<div class="audio-artikel">.*?</div>\n', re.S)


def bersih(fragmen: str) -> str:
    """HTML → teks polos yang enak dibaca mesin."""
    teks = re.sub(r'<[^>]+>', ' ', fragmen)
    teks = htmllib.unescape(teks)
    teks = teks.replace('—', ',').replace('–', ',')
    return re.sub(r'\s+', ' ', teks).strip()


def naskah(html: str) -> str:
    """Susun naskah baca: judul, standfirst, sekilas, lalu isi artikel."""
    bagian = ['Warta Kini.']

    if m := re.search(r'<h1>(.*?)</h1>', html, re.S):
        bagian.append(bersih(m.group(1)) + '.')
    if m := re.search(r'<p class="standfirst">(.*?)</p>', html, re.S):
        bagian.append(bersih(m.group(1)))

    if m := re.search(r'<section class="sekilas">(.*?)</section>', html, re.S):
        poin = [bersih(x) for x in re.findall(r'<li>(.*?)</li>', m.group(1), re.S)]
        if poin:
            bagian.append('Sekilas. ' + ' '.join(p.rstrip('.') + '.' for p in poin))

    if m := re.search(r'<div class="article-body">(.*?)\n    </div>', html, re.S):
        isi = m.group(1)
        isi = re.sub(r'<aside class="baca-juga">.*?</aside>', '', isi, flags=re.S)
        isi = re.sub(r'<div class="article-tags">.*?</div>', '', isi, flags=re.S)
        for blok in re.findall(r'<(h2|p)[^>]*>(.*?)</\1>', isi, re.S):
            if t := bersih(blok[1]):
                bagian.append(t if t.endswith('.') else t + '.')

    bagian.append('Artikel ini ditulis oleh Claude, kecerdasan buatan, '
                  'berdasarkan riset sumber terbuka. Daftar sumber rujukan '
                  'tersedia di halaman artikel.')
    return '\n'.join(bagian)


def durasi(mp3: pathlib.Path) -> str:
    try:
        out = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', str(mp3)],
            capture_output=True, text=True, check=True).stdout.strip()
        total = round(float(out))
        return f'{total // 60}:{total % 60:02d}'
    except Exception:  # noqa: BLE001
        return ''


def main() -> int:
    if not shutil.which('say') or not shutil.which('ffmpeg'):
        print('audio: `say` atau `ffmpeg` tidak tersedia — dilewati.')
        return 0

    AUDIO.mkdir(exist_ok=True)
    hash_file = AUDIO / '.hash.json'
    lama = json.loads(hash_file.read_text()) if hash_file.exists() else {}
    baru: dict[str, str] = {}
    dibuat = dilewati = 0

    for p in sorted(ARTIKEL.glob('*.html')):
        html = p.read_text()
        teks = naskah(html)
        sidik = hashlib.sha256(teks.encode()).hexdigest()[:16]
        baru[p.name] = sidik
        mp3 = AUDIO / f'{p.stem}.mp3'

        if lama.get(p.name) == sidik and mp3.exists():
            dilewati += 1
        else:
            with tempfile.TemporaryDirectory() as tmp:
                src = pathlib.Path(tmp) / 'naskah.txt'
                aiff = pathlib.Path(tmp) / 'suara.aiff'
                src.write_text(teks)
                try:
                    subprocess.run(['say', '-v', SUARA, '-f', str(src),
                                    '-o', str(aiff)], check=True,
                                   capture_output=True)
                    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y',
                                    '-i', str(aiff), '-codec:a', 'libmp3lame',
                                    '-b:a', BITRATE, '-ac', '1', '-ar', '22050',
                                    str(mp3)], check=True, capture_output=True)
                except subprocess.CalledProcessError as e:
                    print(f'audio: gagal membuat {p.stem} ({e}) — dilewati.')
                    baru.pop(p.name, None)
                    continue
            dibuat += 1

        # sisipkan / perbarui pemutar tepat sebelum isi artikel
        html = PLAYER_RE.sub('\n', html)
        panjang = durasi(mp3)
        ket = f' <small>Suara sintetis · {panjang}</small>' if panjang else \
              ' <small>Suara sintetis</small>'
        player = (f'\n    <div class="audio-artikel">\n'
                  f'      <span class="label">Dengarkan artikel{ket}</span>\n'
                  f'      <audio controls preload="none" '
                  f'src="../audio/{p.stem}.mp3"></audio>\n'
                  f'    </div>\n')
        anchor = '\n    <div class="article-body">'
        if anchor in html and 'class="audio-artikel"' not in html:
            html = html.replace(anchor, player + anchor, 1)
        p.write_text(html)

    hash_file.write_text(json.dumps(baru, indent=2))
    print(f'audio: {dibuat} dibuat, {dilewati} dilewati (tak berubah).')
    return 0


if __name__ == '__main__':
    sys.exit(main())

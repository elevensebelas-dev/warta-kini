#!/usr/bin/env python3
"""Kirim ringkasan edisi baru ke channel/grup Telegram.

Kredensial dibaca dari env (TELEGRAM_TOKEN, TELEGRAM_CHAT) atau berkas
~/.config/warta-kini/telegram-token dan ~/.config/warta-kini/telegram-chat.
Tanpa kredensial, script tidak melakukan apa pun (no-op) — pipeline edisi
tetap berjalan normal.
"""
import html as htmllib
import json
import os
import pathlib
import re
import sys
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITUS = 'https://elevensebelas-dev.github.io/warta-kini/'
KONFIG = pathlib.Path.home() / '.config' / 'warta-kini'
MAKS_JUDUL = 6


def rahasia(env: str, berkas: str) -> str | None:
    if nilai := os.environ.get(env):
        return nilai.strip()
    f = KONFIG / berkas
    return f.read_text().strip() if f.exists() else None


def teks(fragmen: str) -> str:
    return re.sub(r'\s+', ' ', htmllib.unescape(
        re.sub(r'<[^>]+>', ' ', fragmen))).strip()


def susun_pesan() -> str | None:
    index = ROOT / 'index.html'
    if not index.exists():
        return None
    html = index.read_text()

    tanggal = ''
    if m := re.search(r'<strong>(.*?)</strong>', html, re.S):
        tanggal = teks(m.group(1))

    baris = [f'<b>Warta Kini — Edisi {htmllib.escape(tanggal)}</b>', '']

    if m := re.search(r'<h1><a href="(.*?)">(.*?)</a></h1>', html, re.S):
        baris.append(f'📌 <a href="{SITUS}{m.group(1)}">'
                     f'{htmllib.escape(teks(m.group(2)))}</a>')
        baris.append('')

    lain = re.findall(r'<h2><a href="(.*?)">(.*?)</a></h2>', html, re.S)
    for url, judul in lain[:MAKS_JUDUL]:
        baris.append(f'• <a href="{SITUS}{url}">{htmllib.escape(teks(judul))}</a>')

    baris += ['', f'<a href="{SITUS}">Baca edisi lengkap</a> · '
                  'Seluruh artikel ditulis oleh AI berdasarkan riset sumber terbuka.']
    return '\n'.join(baris)


def main() -> int:
    token = rahasia('TELEGRAM_TOKEN', 'telegram-token')
    chat = rahasia('TELEGRAM_CHAT', 'telegram-chat')
    if not token or not chat:
        print('telegram: kredensial belum dipasang — dilewati.')
        return 0

    pesan = susun_pesan()
    if not pesan:
        print('telegram: index.html tidak terbaca — dilewati.')
        return 0

    muatan = json.dumps({
        'chat_id': chat,
        'text': pesan,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }).encode()
    req = urllib.request.Request(
        f'https://api.telegram.org/bot{token}/sendMessage',
        data=muatan, headers={'Content-Type': 'application/json'})

    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            hasil = json.load(r)
    except urllib.error.HTTPError as e:
        print(f'telegram: ditolak API ({e.code}) — {e.read()[:200]!r}')
        return 0
    except Exception as e:  # noqa: BLE001 — kegagalan kirim tak boleh menggagalkan edisi
        print(f'telegram: gagal mengirim ({e}) — dilewati.')
        return 0

    print('telegram: ringkasan edisi terkirim.' if hasil.get('ok')
          else f'telegram: API menolak — {hasil}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

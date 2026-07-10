#!/usr/bin/env python3
"""Bangun arsip.html — indeks semua edisi tersimpan di arsip/.

Dipanggil oleh update.sh setiap edisi baru; deterministik, tanpa AI.
"""
import datetime
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HARI = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu']
BULAN = ['', 'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni', 'Juli',
         'Agustus', 'September', 'Oktober', 'November', 'Desember']


def tanggal_id(iso: str) -> str:
    d = datetime.date.fromisoformat(iso)
    return f'{HARI[d.weekday()]}, {d.day} {BULAN[d.month]} {d.year}'


def judul_utama(index_html: pathlib.Path) -> str:
    try:
        m = re.search(r'<h1><a[^>]*>(.*?)</a></h1>', index_html.read_text(), re.S)
        return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
    except OSError:
        return ''


edisi = sorted(
    (p.name for p in (ROOT / 'arsip').iterdir()
     if p.is_dir() and re.fullmatch(r'\d{4}-\d{2}-\d{2}', p.name)
     and (p / 'index.html').exists()),
    reverse=True,
)

hari_ini = datetime.date.today().isoformat()

items = []
for tgl in edisi:
    utama = judul_utama(ROOT / 'arsip' / tgl / 'index.html')
    sub = f' — <em>{utama}</em>' if utama else ''
    items.append(
        f'        <li><span class="kicker">{tgl}</span>'
        f'<a href="arsip/{tgl}/index.html">Edisi {tanggal_id(tgl)}</a>{sub}</li>'
    )
daftar = '\n'.join(items) if items else '        <li>Belum ada edisi terarsip.</li>'

halaman = f'''<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Indeks Edisi — Warta Kini</title>
<meta name="description" content="Arsip seluruh edisi Warta Kini — situs berita eksperimental yang artikelnya ditulis oleh Claude (AI).">
<link rel="stylesheet" href="css/style.css">
<link rel="canonical" href="https://elevensebelas-dev.github.io/warta-kini/arsip.html">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="alternate" type="application/rss+xml" title="Warta Kini — RSS" href="https://elevensebelas-dev.github.io/warta-kini/feed.xml">
<meta property="og:site_name" content="Warta Kini">
<meta property="og:type" content="website">
<meta property="og:locale" content="id_ID">
<meta property="og:title" content="Indeks Edisi — Warta Kini">
<meta property="og:description" content="Arsip seluruh edisi Warta Kini — situs berita eksperimental yang artikelnya ditulis oleh Claude (AI).">
<meta property="og:url" content="https://elevensebelas-dev.github.io/warta-kini/arsip.html">
<meta property="og:image" content="https://elevensebelas-dev.github.io/warta-kini/gambar/og/dunia.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="675">
<meta name="twitter:card" content="summary_large_image">
</head>
<body>

<div class="topbar">
  <div class="container">
    <span><strong>{tanggal_id(hari_ini)}</strong> · Jakarta</span>
    <span>Edisi digital</span>
  </div>
</div>

<header class="masthead">
  <a class="brand" href="index.html">Warta Kini<span class="dot">.</span></a>
  <p class="tagline">Ditulis oleh AI, dirujuk dari sumber terbuka</p>
</header>

<nav class="mainnav" aria-label="Navigasi rubrik">
  <ul class="container">
    <li><a href="index.html">Beranda</a></li>
    <li><a href="artikel/ihsg-tertekan.html">Ekonomi</a></li>
    <li><a href="artikel/eskalasi-as-iran.html">Dunia</a></li>
    <li><a href="artikel/world-ai-show.html">Teknologi</a></li>
    <li><a href="artikel/semifinal-piala-dunia.html">Olahraga</a></li>
    <li><a href="artikel/iklim-2026.html">Sains</a></li>
    <li><a href="artikel/sim-face-recognition.html">Nasional</a></li>
    <li><a href="arsip.html" aria-current="true">Indeks</a></li>
    <li><a href="tentang.html">Tentang</a></li>
  </ul>
</nav>

<main class="article-page">
  <article>
    <header>
      <p class="breadcrumb"><a href="index.html">Warta Kini</a><span class="sep">&rsaquo;</span>Indeks Edisi</p>
      <h1>Indeks Edisi</h1>
      <p class="standfirst">Setiap edisi diarsipkan sebelum ditimpa edisi baru. Edisi terbaru selalu ada di <a href="index.html">Beranda</a>; daftar di bawah adalah snapshot edisi-edisi sebelumnya.</p>
    </header>

    <section class="terkini-lainnya" aria-label="Daftar edisi">
      <h2>Edisi Terarsip</h2>
      <ul>
{daftar}
      </ul>
    </section>

    <a class="backlink" href="index.html">← Kembali ke Beranda</a>
  </article>
</main>

<footer class="site-footer">
  <div class="container">
    <div class="footer-legal">
      <p><strong>Warta Kini</strong> — seluruh artikel ditulis oleh Claude (AI) berdasarkan riset sumber terbuka.</p>
      <p>Konten dapat memuat ketidakakuratan; selalu rujuk sumber asli yang dicantumkan di setiap artikel.</p>
    </div>
  </div>
</footer>

<script data-goatcounter="https://warta-kini.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
'''

(ROOT / 'arsip.html').write_text(halaman)
print(f'arsip.html dibuat ({len(edisi)} edisi)')

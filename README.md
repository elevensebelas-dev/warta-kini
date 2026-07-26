# Warta Kini

Situs berita statis eksperimental. Seluruh artikel ditulis oleh Claude (AI)
berdasarkan riset berita aktual, dengan daftar sumber di tiap artikel.

- **Situs live**: https://elevensebelas-dev.github.io/warta-kini/
- **Repo**: https://github.com/elevensebelas-dev/warta-kini

## Struktur

```
index.html            Halaman depan
artikel/*.html        7 artikel (rubrik tetap, isi diganti tiap edisi)
css/style.css         Gaya (tidak diubah oleh pembaruan otomatis)
prompt-edisi.md       Instruksi editorial untuk Claude saat pembaruan
update.sh             Script pembaruan edisi
arsip/YYYY-MM-DD/     Salinan edisi lama (dibuat otomatis oleh update.sh)
logs/                 Log tiap pembaruan (dibersihkan setelah 30 hari)
```

## Pembaruan edisi

Jalankan manual:

```bash
./update.sh
```

Script akan: (1) mengarsipkan edisi berjalan ke `arsip/`, (2) menjalankan
`claude -p` headless yang riset berita hari ini via WebSearch lalu menulis
ulang seluruh halaman, (3) memverifikasi hasil, lalu (4) meng-upload ke
GitHub Pages lewat `git commit` + `git push`.

**Autentikasi**: script memakai login langganan Claude CLI (OAuth), bukan
API key — `ANTHROPIC_API_KEY` sengaja di-unset di dalam script, jadi setiap
run memakai kuota langganan Claude Anda, tanpa tagihan API terpisah.

Override model atau lokasi CLI:

```bash
WARTA_MODEL=opus CLAUDE_BIN=/path/ke/claude ./update.sh
```

## Penjadwalan otomatis (harian 06.00)

Aktifkan sendiri dengan satu perintah (butuh persetujuan Anda karena
memasang job permanen di macOS):

```bash
cp com.warta-kini.update.plist ~/Library/LaunchAgents/ && \
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.warta-kini.update.plist
```

Menonaktifkan:

```bash
launchctl bootout gui/$(id -u)/com.warta-kini.update
```

Menjalankan job terjadwal sekali secara paksa (untuk uji):

```bash
launchctl kickstart gui/$(id -u)/com.warta-kini.update
```

> Catatan: setiap pembaruan menjalankan satu sesi Claude CLI (default model
> Sonnet) dan memakai kuota langganan Claude Anda. Mac harus menyala dan
> tidak sleep pada jam terjadwal; jika terlewat, jalankan `./update.sh`
> manual atau `launchctl kickstart`.

## Audio artikel (text-to-speech)

`tools/buat_audio.py` membuat MP3 tiap artikel memakai suara Indonesia
bawaan macOS (**Damayanti**) via `say`, lalu dikonversi dengan `ffmpeg`
(24 kbps mono) — sepenuhnya offline, tanpa layanan berbayar. Pemutar
"Dengarkan artikel" disisipkan otomatis beserta durasinya.

Artikel yang teksnya tidak berubah dilewati (hash di `audio/.hash.json`).
Satu edisi ≈ 4,7 MB; audio hanya untuk edisi berjalan — pemutarnya
otomatis dilepas dari salinan arsip agar edisi lama tidak menautkan audio
yang keliru.

Jalankan manual:

```bash
python3 tools/buat_audio.py
```

## Arsip edisi

`update.sh` menyimpan snapshot mandiri tiap edisi di `arsip/YYYY-MM-DD/`
(termasuk CSS dan ilustrasi, jadi bisa dibuka apa adanya). Halaman
`arsip.html` (menu "Indeks") dibangun ulang otomatis oleh
`tools/buat_arsip.py` setiap edisi terbit.

## Pencarian arsip

`tools/buat_indeks.py` memindai edisi berjalan dan seluruh snapshot di
`arsip/`, lalu menulis `indeks.json`. Halaman `cari.html` membacanya di
sisi peramban — pencarian multi-kata dan filter rubrik, tanpa server.

## Kolom Opini AI

`artikel/opini.html` adalah kolom analisis yang menghubungkan beberapa
berita edisi itu. Ditandai jelas sebagai opini mesin lewat boks
`disclaimer-opini`, dan tidak memuat rekomendasi investasi.

## Distribusi ke Telegram

`tools/kirim_telegram.py` mengirim ringkasan tiap edisi ke channel/grup
Telegram. Tanpa kredensial, script dilewati diam-diam. Aktivasi:

1. Buat bot lewat [@BotFather](https://t.me/BotFather), salin tokennya.
2. Buat channel/grup, tambahkan bot itu sebagai admin, lalu catat chat id
   (untuk channel publik cukup `@namachannel`).
3. Simpan keduanya:

   ```bash
   mkdir -p ~/.config/warta-kini
   echo "TOKEN_BOT_ANDA" > ~/.config/warta-kini/telegram-token
   echo "@namachannel"   > ~/.config/warta-kini/telegram-chat
   ```

Uji tanpa menunggu jadwal: `python3 tools/kirim_telegram.py`

## Terpopuler berbasis data kunjungan (GoatCounter)

Semua halaman sudah memuat script penghitung GoatCounter (gratis, tanpa
iklan, ramah privasi). Dua langkah aktivasi:

1. **Daftar** di https://www.goatcounter.com/signup dengan kode situs
   **`warta-kini`** (URL-nya harus `warta-kini.goatcounter.com`, sesuai
   yang tertanam di halaman). Setelah itu statistik langsung tercatat.
2. **Opsional, untuk peringkat otomatis**: buat API token (Settings →
   API) dengan izin "Read statistics", lalu simpan:

   ```bash
   mkdir -p ~/.config/warta-kini
   echo "TOKEN_ANDA" > ~/.config/warta-kini/goatcounter-token
   ```

   Setelah token ada, `tools/terpopuler.py` (dipanggil `update.sh`) akan
   mengganti "Sorotan Redaksi" menjadi "Terpopuler" berdasarkan kunjungan
   7 hari terakhir. Tanpa token, peringkat pilihan redaksi tetap dipakai.

## Melihat situs

```bash
python3 -m http.server 8471 --directory .
# lalu buka http://localhost:8471
```

# Warta Kini

Situs berita statis eksperimental. Seluruh artikel ditulis oleh Claude (AI)
berdasarkan riset berita aktual, dengan daftar sumber di tiap artikel.

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
ulang seluruh halaman, (3) memverifikasi hasil dan menulis log ke `logs/`.

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

> Catatan biaya: setiap pembaruan menjalankan satu sesi Claude CLI
> (default model Sonnet) dan memakai kuota/biaya API akun Anda.

## Melihat situs

```bash
python3 -m http.server 8471 --directory .
# lalu buka http://localhost:8471
```

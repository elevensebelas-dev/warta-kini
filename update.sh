#!/usr/bin/env bash
# Warta Kini — pembaruan edisi otomatis.
# 1. Mengarsipkan edisi berjalan
# 2. Menjalankan Claude CLI (headless, login langganan — BUKAN API key)
#    untuk riset berita aktual dan menulis ulang seluruh halaman
# 3. Meng-upload hasil ke GitHub Pages (git commit + push)
#
# Pemakaian:  ./update.sh
# Override:   CLAUDE_BIN=/path/ke/claude WARTA_MODEL=opus ./update.sh
set -euo pipefail

SITE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_BIN="${CLAUDE_BIN:-/Users/hibarherdiana/.local/bin/claude}"
WARTA_MODEL="${WARTA_MODEL:-sonnet}"

# Paksa Claude CLI memakai login langganan (OAuth), bukan API key,
# meskipun environment kebetulan membawa variabel API.
unset ANTHROPIC_API_KEY ANTHROPIC_AUTH_TOKEN 2>/dev/null || true

STAMP="$(date +%Y-%m-%d)"
LOG_DIR="$SITE_DIR/logs"
LOG_FILE="$LOG_DIR/update-$(date +%Y%m%d-%H%M%S).log"
ARCHIVE_DIR="$SITE_DIR/arsip/$STAMP"

mkdir -p "$LOG_DIR" "$ARCHIVE_DIR"

# --- 1. Arsipkan edisi berjalan sebelum ditimpa (snapshot mandiri) ---
cp "$SITE_DIR/index.html" "$SITE_DIR/tentang.html" "$SITE_DIR/favicon.svg" \
   "$SITE_DIR/apple-touch-icon.png" "$ARCHIVE_DIR/" 2>/dev/null || true
cp -R "$SITE_DIR/artikel" "$ARCHIVE_DIR/" 2>/dev/null || true
mkdir -p "$ARCHIVE_DIR/css" "$ARCHIVE_DIR/gambar"
cp "$SITE_DIR/css/style.css" "$ARCHIVE_DIR/css/" 2>/dev/null || true
cp "$SITE_DIR"/gambar/*.svg "$ARCHIVE_DIR/gambar/" 2>/dev/null || true

# Rapikan snapshot arsip: lepas pemutar audio (audio hanya untuk edisi
# berjalan) dan arahkan tautan berkas situs-wide ke URL langsung.
python3 - "$ARCHIVE_DIR" <<'PY' 2>/dev/null || true
import pathlib, re, sys
SITUS = 'https://elevensebelas-dev.github.io/warta-kini/'
akar = pathlib.Path(sys.argv[1])
for p in [*akar.glob('*.html'), *(akar / 'artikel').glob('*.html')]:
    t = asli = p.read_text()
    t = re.sub(r'\n?\s*<div class="audio-artikel">.*?</div>\n', '\n', t, flags=re.S)
    for berkas in ('feed.xml', 'cari.html', 'arsip.html'):
        t = re.sub(rf'href="(?:\.\./)?{re.escape(berkas)}"', f'href="{SITUS}{berkas}"', t)
    if t != asli:
        p.write_text(t)
PY

echo "[$(date '+%F %T')] Mulai pembaruan edisi $STAMP (model: $WARTA_MODEL)" | tee -a "$LOG_FILE"

# --- 2. Tulis edisi baru dengan Claude CLI ---
cd "$SITE_DIR"
"$CLAUDE_BIN" -p "$(cat "$SITE_DIR/prompt-edisi.md")

Tanggal hari ini (ISO): $STAMP" \
  --model "$WARTA_MODEL" \
  --permission-mode acceptEdits \
  --allowedTools "WebSearch WebFetch" \
  >> "$LOG_FILE" 2>&1

# Pemeriksaan hasil: tahun berjalan harus muncul di halaman depan
TAHUN="$(date +%Y)"
if ! grep -q "$TAHUN" "$SITE_DIR/index.html"; then
  echo "[$(date '+%F %T')] PERINGATAN: index.html tampak tidak diperbarui — upload dibatalkan, periksa $LOG_FILE" | tee -a "$LOG_FILE"
  exit 1
fi
echo "[$(date '+%F %T')] Edisi baru selesai ditulis. Arsip: arsip/$STAMP" | tee -a "$LOG_FILE"

# --- 2b. Audio artikel, indeks arsip, peringkat Terpopuler (deterministik) ---
python3 "$SITE_DIR/tools/buat_audio.py" >> "$LOG_FILE" 2>&1 || true
python3 "$SITE_DIR/tools/buat_arsip.py" >> "$LOG_FILE" 2>&1 || true
python3 "$SITE_DIR/tools/buat_indeks.py" >> "$LOG_FILE" 2>&1 || true
python3 "$SITE_DIR/tools/terpopuler.py" >> "$LOG_FILE" 2>&1 || true

# --- 3. Upload ke GitHub Pages ---
if [ -d "$SITE_DIR/.git" ]; then
  git -C "$SITE_DIR" add -A >> "$LOG_FILE" 2>&1
  if git -C "$SITE_DIR" diff --cached --quiet; then
    echo "[$(date '+%F %T')] Tidak ada perubahan untuk di-upload." | tee -a "$LOG_FILE"
  else
    git -C "$SITE_DIR" commit -m "Edisi $STAMP" >> "$LOG_FILE" 2>&1
    if git -C "$SITE_DIR" push origin main >> "$LOG_FILE" 2>&1; then
      echo "[$(date '+%F %T')] Terunggah ke GitHub Pages." | tee -a "$LOG_FILE"
    else
      echo "[$(date '+%F %T')] PERINGATAN: push gagal — edisi tetap tersimpan lokal, periksa $LOG_FILE" | tee -a "$LOG_FILE"
      exit 1
    fi
  fi
else
  echo "[$(date '+%F %T')] Repo git belum ada — upload dilewati." | tee -a "$LOG_FILE"
fi

# --- 4. Sebarkan ringkasan edisi (no-op bila kredensial belum dipasang) ---
python3 "$SITE_DIR/tools/kirim_telegram.py" >> "$LOG_FILE" 2>&1 || true

echo "[$(date '+%F %T')] Selesai. Log: $LOG_FILE" | tee -a "$LOG_FILE"

# Bersihkan log lebih tua dari 30 hari
find "$LOG_DIR" -name 'update-*.log' -mtime +30 -delete 2>/dev/null || true

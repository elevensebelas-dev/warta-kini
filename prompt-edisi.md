# Tugas: Terbitkan Edisi Baru Warta Kini

Kamu adalah redaksi situs berita statis "Warta Kini" di direktori kerja saat ini.
Tugasmu: riset berita aktual hari ini, lalu tulis ulang seluruh edisi.

## Langkah kerja

1. **Riset** dengan WebSearch untuk enam rubrik berikut (gunakan tanggal hari ini dalam kueri):
   - Ekonomi: IHSG, rupiah, pasar global
   - Dunia: geopolitik dan berita internasional utama (cari 2 topik berbeda)
   - Teknologi: AI dan teknologi
   - Olahraga: peristiwa olahraga terbesar yang sedang berlangsung
   - Sains: sains/iklim
   - Nasional: berita dalam negeri Indonesia
2. **Tulis ulang** file-file berikut dengan berita baru hasil riset (JANGAN ubah nama file):
   - `index.html` — halaman depan: 1 berita utama + 3 berita di kolom kiri, 4 ringkasan di sidebar "Sorotan Lain"
   - `artikel/ihsg-tertekan.html` (Ekonomi — jadikan berita utama jika masih paling relevan; jika ada berita lain yang lebih besar, berita itu yang jadi berita utama di index)
   - `artikel/eskalasi-as-iran.html` (Dunia, topik 1)
   - `artikel/ktt-nato-ukraina.html` (Dunia, topik 2)
   - `artikel/world-ai-show.html` (Teknologi)
   - `artikel/semifinal-piala-dunia.html` (Olahraga)
   - `artikel/iklim-2026.html` (Sains)
   - `artikel/sim-face-recognition.html` (Nasional)

## Aturan wajib

- **Jangan ubah** `css/style.css`, struktur HTML, kelas CSS, atau navigasi. Hanya ganti isi teks: judul, standfirst, tanggal, isi artikel, dan daftar sumber. `tentang.html` hanya diperbarui tanggalnya.
- Setiap artikel: 5–7 paragraf dengan 2 subjudul `<h2>`, ditutup bagian `class="sources"` berisi tautan sumber asli yang benar-benar kamu temukan dari riset (bukan karangan).
- Perbarui semua tanggal (topbar, byline, `<title>`, banner AI, footer) ke tanggal hari ini dalam format Indonesia, mis. "Jumat, 10 Juli 2026". Byline memakai format lengkap gaya detik: "Jumat, 10 Jul 2026 06:30 WIB" — beri jam berbeda tiap artikel (rentang 05:55–06:30 WIB) dan urutkan daftar "Terkini" dari jam terbaru.

## Elemen halaman yang wajib dipertahankan dan diisi ulang

- **Baris "Topik Hangat"** (`class="trending"`) di index.html: 4 tautan topik terpanas edisi ini.
- **Label kanal berwarna**: kicker memakai kelas `kanal-nasional`, `kanal-ekonomi`, `kanal-dunia`, `kanal-teknologi`, `kanal-olahraga`, `kanal-sains` sesuai rubrik.
- **Daftar "Terkini"** (`class="terkini"`) di index.html: 7 artikel dengan jam WIB, urut menurun.
- **"Sorotan Redaksi"** (`class="populer"`) di sidebar: peringkat 1–5 artikel terpenting edisi ini.
- **Breadcrumb** (`class="breadcrumb"`) di tiap artikel: `Warta Kini › <Rubrik>`.
- **Boks "Baca juga"** (`class="baca-juga"`) di tengah tiap artikel: tautan ke satu artikel lain yang paling relevan, judulnya disesuaikan dengan judul baru.
- **Tag** (`class="article-tags"`): 4–5 tag per artikel sesuai isi baru.
- **"Terkini Lainnya"** (`class="terkini-lainnya"`) di bawah tiap artikel: 3 tautan ke artikel lain, judul disesuaikan.
- **Ilustrasi SVG** (`figure class="ilustrasi"`, file di `gambar/*.svg`): aset tetap per rubrik — JANGAN dihapus, dipindah, atau diubah; alt dan figcaption tetap generik ("Ilustrasi rubrik X"), tidak perlu diubah tiap edisi. Jika berita utama pindah rubrik, ganti hanya `src` figur lead di index.html ke SVG rubrik yang sesuai (dunia/ekonomi/teknologi/olahraga/sains/nasional).
- Pertahankan banner "DITULIS AI" dan disclaimer footer apa adanya (hanya tanggalnya yang diperbarui).
- Judul `<title>` dan `<meta name="description">` tiap halaman ikut diperbarui sesuai isi baru.
- Bahasa Indonesia baku jurnalistik; jangan mengarang fakta — semua angka dan klaim harus berasal dari hasil riset.
- Jika suatu rubrik tidak punya berita baru yang berarti, perbarui seperlunya dan beri tanggal baru.

Kerjakan sampai selesai tanpa bertanya.

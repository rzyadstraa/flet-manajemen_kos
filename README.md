# Smart Boarding House - Manajemen Kos

Aplikasi desktop untuk mengelola operasional rumah kos. Aplikasi dibuat dengan Python dan Flet, menggunakan MySQL sebagai database.

## Fitur

- Login dengan hak akses admin dan pemilik.
- Dashboard ringkasan kamar, penghuni, dan tagihan.
- Pengelolaan data kamar dan penghuni.
- Pengelolaan tagihan bulanan serta prediksi biaya listrik menggunakan Linear Regression.
- Pembuatan laporan tagihan dalam format PDF.
- Pengelolaan profil akun.

## Teknologi

- Python 3.12
- Flet 1.1.2 dan Flet Charts 1.1.2
- MySQL atau MariaDB
- pandas dan scikit-learn untuk prediksi
- ReportLab untuk membuat laporan PDF

## Persiapan

1. Pasang Python 3.12 dan MySQL. Untuk Windows, MySQL dapat dijalankan melalui XAMPP.
2. Aktifkan layanan MySQL dari XAMPP Control Panel.
3. Buat virtual environment dan pasang dependensi:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install --upgrade pip
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

4. Buat database dan tabel dengan mengimpor [`manajemenkos.sql`](./manajemenkos.sql):
   - Buka phpMyAdmin.
   - Pilih **Import**, pilih file `manajemenkos.sql`, lalu jalankan import.
   - File SQL membuat database `db_manajemenkos` beserta tabel dan data contoh.

   Jalankan import satu kali pada database baru. File tersebut juga memasukkan data contoh dan tidak dirancang untuk diimpor berulang kali.

## Menjalankan aplikasi

Dari folder proyek, jalankan:

```powershell
.\.venv\Scripts\python.exe main.py
```

Di VS Code, pilih interpreter `.\.venv\Scripts\python.exe` melalui **Python: Select Interpreter** agar Pylance dan aplikasi memakai environment yang sama.

## Akun demo

| Hak akses | Username | Password |
|---|---|---|
| Admin | `admin` | `123` |
| Pemilik | `pemilik` | `123` |

Akun ini dibuat oleh skrip SQL untuk keperluan demo. Jangan gunakan kredensial tersebut untuk penerapan produksi.

## Konfigurasi database

Koneksi database saat ini menggunakan konfigurasi berikut:

- Host: `localhost`
- User: `root`
- Password: kosong
- Database: `db_manajemenkos`

Jika konfigurasi MySQL berbeda, sesuaikan fungsi `koneksi_database()` pada modul yang mengakses database, seperti `hal_login.py`, `hal_dashboard.py`, `hal_kamar.py`, `hal_penghuni.py`, `hal_tagihan.py`, `hal_profil.py`, dan `hal_laporan.py`.

## Struktur proyek

```text
main.py             Entry point dan navigasi aplikasi
hal_login.py        Login dan pencatatan akses terakhir
hal_dashboard.py    Dashboard ringkasan
hal_kamar.py        Pengelolaan kamar
hal_penghuni.py     Pengelolaan penghuni
hal_tagihan.py      Pengelolaan tagihan dan prediksi biaya listrik
hal_laporan.py      Pembuatan laporan PDF
hal_profil.py       Perubahan profil akun
hal_tentang.py      Informasi aplikasi
manajemenkos.sql    Skema database dan data contoh
requirements.txt    Dependensi Python
```

## Pemecahan masalah

- **Modul tidak ditemukan**: pastikan dependensi terpasang di virtual environment proyek dan interpreter VS Code mengarah ke `.venv`.
- **Gagal terhubung ke database**: pastikan MySQL aktif, database sudah diimpor, dan konfigurasi koneksi sesuai.
- **Akses database ditolak**: periksa user dan password MySQL pada fungsi `koneksi_database()`.

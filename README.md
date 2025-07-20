# MamboChaCha - File Encryption and Decryption Web App (Kelompok 6)

**MamboChaCha** adalah aplikasi web sederhana untuk mengenkripsi dan mendekripsi file menggunakan algoritma enkripsi stream cipher ChaCha20. Website ini memungkinkan pengguna mengenkripsi file, menghasilkan file `.enc`, serta QR Code berisi key dan nonce. Dekripsi dapat dilakukan dengan mengunggah file `.enc` beserta QR Code, baik melalui input manual maupun scan kamera.

---

## Anggota Kelompok
1. Yosua Nathanael Latuputty
2. Muhammad Zidan Rizki Zulfazli
3. Urdha Egha Kirana
---

## 📂 Struktur Folder

```
.
├── app.py                  # Flask App utama
├── encrypt.py              # Logic enkripsi file ChaCha20
├── decrypt.py              # Logic dekripsi file ChaCha20
├── qrgen.py                # Pembuatan dan pembacaan QR Code key+nonce
├── static/
│   ├── assets/             # Gambar logo dan ilustrasi
│   │   ├── Logo Mambo ChaCha.png
│   │   ├── Rectangle 1.png
│   │   └── image.png
│   ├── decrypt.css         # CSS untuk halaman decrypt
│   ├── encrypt.css         # CSS untuk halaman encrypt
│   └── main.css            # CSS utama
├── templates/
│   ├── decrypt.html        # Tampilan dekripsi
│   ├── encrypt.html        # Tampilan enkripsi
│   └── index.html          # Halaman utama
├── requirements.txt        # Dependency Python
└── README.md               # Dokumentasi proyek
```

---

## ⚙️ Fitur

* **Enkripsi File dengan ChaCha20**
  Mengunggah file apapun (`json`, `txt`, `mp3`, `jpg`, `jpeg`, `pdf`, `mp4`,
    `zip`, `tar`, `docx`), aplikasi akan mengenkripsi file menjadi `.enc` dan mengeluarkan QR Code yang berisi key dan nonce dalam format aman.

* **Dekripsi File**
  Mengunggah `.enc` file beserta QR Code untuk mengembalikan file asli. QR Code dapat di-scan via kamera atau dimasukkan manual.

* **Antarmuka Web Sederhana**
  Tersedia halaman utama, halaman enkripsi, dan halaman dekripsi yang responsif dan mudah digunakan.

---

## 🚀 Cara Menjalankan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Flask App

```bash
python app.py
```

Aplikasi akan berjalan di [http://127.0.0.1:5000](http://127.0.0.1:5000)

---
## 🖥️ Versi Python

Direkomendasikan menggunakan **Python 3.13**

---
## 🖥️ Website Vercel

https://chacha20-audio-encryption.vercel.app/

---
## 🖥️ Repositori Github

https://github.com/yosualatuputty/chacha20-audio-encryption

---

## 📦 Requirements

```
blinker==1.9.0
click==8.2.1
colorama==0.4.6
Flask==3.1.1
itsdangerous==2.2.0
Jinja2==3.1.6
MarkupSafe==3.0.2
numpy==2.2.6
pillow==11.3.0
pycryptodome==3.23.0
qrcode==8.2
Werkzeug==3.1.3
```

---

## 📌 Catatan Penggunaan

* 🔒 **Enkripsi File** → Menghasilkan file `.enc` + QR Code (key dan nonce)
* 🔓 **Dekripsi File** → Mengembalikan file asli sebelum enkripsi berdasarkan file `.enc` + QR Code
* Tidak ada file yang disimpan di server secara permanen.

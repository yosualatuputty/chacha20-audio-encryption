from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import os

def encrypt_file(input_path, output_dir='uploads'):
    """
    Enkripsi file menggunakan ChaCha20.
    Mengembalikan path ciphertext, path key_nonce, key, nonce, dan ekstensi asli.
    """
    # Baca file sebagai byte
    with open(input_path, 'rb') as f:
        file_data = f.read()

    # Buat key dan nonce
    key = get_random_bytes(32)   # 256-bit key
    nonce = get_random_bytes(8)  # 64-bit nonce

    # Enkripsi
    cipher = ChaCha20.new(key=key, nonce=nonce)
    ciphertext = cipher.encrypt(file_data)

    # Siapkan nama file
    name, ext = os.path.splitext(os.path.basename(input_path))
    encrypted_filename = os.path.join(output_dir, f"{name}.enc")
    key_nonce_filename = os.path.join(output_dir, f"{name}_key_nonce.bin")

    # Simpan ciphertext
    with open(encrypted_filename, 'wb') as f:
        f.write(ciphertext)

    # Simpan key + nonce (opsional kalau ingin simpan dalam file terpisah)
    with open(key_nonce_filename, 'wb') as f:
        f.write(key + nonce)

    # Kembalikan hasil
    return encrypted_filename, key, nonce, ext

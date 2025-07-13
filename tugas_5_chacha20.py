from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes
import os

from google.colab import files
uploaded = files.upload()  # User upload file

filename = list(uploaded.keys())[0]
print(f"\n File yang diunggah: {filename}")

# baca file sebagai byte
with open(filename, 'rb') as f:
    file_data = f.read()

print("Ukuran file:", len(file_data), "byte")
print("Plaintext (ASCII):", file_data[:16])
print("Plaintext (Hex):", file_data[:16].hex())

# buat key dan nonce
key = get_random_bytes(32)      # 32-byte = 256-bit
nonce = get_random_bytes(8)     # 8-byte = 64-bit
print("Key (hex):", key.hex())
print("Nonce (hex):", nonce.hex())

# enkripsi file
cipher_enc = ChaCha20.new(key=key, nonce=nonce)
ciphertext = cipher_enc.encrypt(file_data)

# simpan file enkripsi dan key_nonce
encrypted_filename = filename + ".enc"
with open(encrypted_filename, 'wb') as f:
    f.write(ciphertext)

with open("key_nonce.bin", 'wb') as f:
    f.write(key + nonce)

print("\n Ciphertext (Hex, 16 byte pertama):", ciphertext[:16].hex())

files.download("key_nonce.bin")
files.download(encrypted_filename)

# visualisasi XOR
cipher_temp = ChaCha20.new(key=key, nonce=nonce)
keystream = cipher_temp.encrypt(b'\x00' * len(file_data))

print("\n Perbandingan XOR Byte:")
print("Index | Plaintext | Keystream | Ciphertext")
print("-" * 48)
for i in range(16):
    p = file_data[i]
    k = keystream[i]
    c = ciphertext[i]
    print(f"{i:5} |    {p:02X}    |    {k:02X}     |     {c:02X}")

# baca key dan nonce
with open("key_nonce.bin", 'rb') as f:
    data = f.read()
    key_dec = data[:32]
    nonce_dec = data[32:]

# baca file terenkripsi
with open(encrypted_filename, 'rb') as f:
    ciphertext = f.read()

# dekripsi
cipher_dec = ChaCha20.new(key=key_dec, nonce=nonce_dec)
decrypted_data = cipher_dec.decrypt(ciphertext)

# simpan hasil dekripsi
name, ext = os.path.splitext(filename)
decrypted_filename = f"{name}_decrypted{ext}"
with open(decrypted_filename, 'wb') as f:
    f.write(decrypted_data)

print("\n Dekripsi selesai.")
print(" File didekripsi sebagai:", decrypted_filename)

files.download(decrypted_filename)
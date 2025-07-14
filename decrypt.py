import os
import json
import cv2
from Crypto.Cipher import ChaCha20

def extract_key_nonce_from_qr_opencv(qr_path):
    img = cv2.imread(qr_path)
    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if not data:
        raise ValueError("QR Code tidak terbaca.")

    parsed = json.loads(data.replace("'", "\""))
    key = bytes.fromhex(parsed['key'])
    nonce = bytes.fromhex(parsed['nonce'])
    ext = parsed.get('ext', '')  # Ekstensi asli (misal: .mp3)
    return key, nonce, ext


def decrypt_file(qr_path, encrypted_path, output_dir='uploads'):
    key, nonce, ext = extract_key_nonce_from_qr_opencv(qr_path)

    with open(encrypted_path, 'rb') as f:
        ciphertext = f.read()

    cipher = ChaCha20.new(key=key, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    name, _ = os.path.splitext(os.path.basename(encrypted_path))
    output_name = name + ext  # Pastikan nama akhir punya ekstensi asli

    output_path = os.path.join(output_dir, output_name)
    with open(output_path, 'wb') as f:
        f.write(plaintext)

    return output_path

def decrypt_file_camera(qr_data, encrypted_path, output_dir='uploads'):
    parsed = json.loads(qr_data.replace("'", "\""))
    key = bytes.fromhex(parsed['key'])
    nonce = bytes.fromhex(parsed['nonce'])
    ext = parsed.get('ext', '')  # Ekstensi asli (misal: .mp3)

    with open(encrypted_path, 'rb') as f:
        ciphertext = f.read()

    cipher = ChaCha20.new(key=key, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    name, _ = os.path.splitext(os.path.basename(encrypted_path))
    output_name = name + ext  # Pastikan nama akhir punya ekstensi asli

    output_path = os.path.join(output_dir, output_name)
    with open(output_path, 'wb') as f:
        f.write(plaintext)

    return output_path

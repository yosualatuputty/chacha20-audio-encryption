import os
import json
from Crypto.Cipher import ChaCha20


def decrypt_file_camera(qr_string, encrypted_path, output_dir="/tmp"):
    parsed = json.loads(qr_string.replace("'", "\""))
    key = bytes.fromhex(parsed['key'])
    nonce = bytes.fromhex(parsed['nonce'])
    ext = parsed.get('ext', '')

    with open(encrypted_path, 'rb') as f:
        ciphertext = f.read()

    cipher = ChaCha20.new(key=key, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)

    name, _ = os.path.splitext(os.path.basename(encrypted_path))
    output_name = name + ext
    output_path = os.path.join(output_dir, output_name)

    with open(output_path, 'wb') as f:
        f.write(plaintext)

    return output_path

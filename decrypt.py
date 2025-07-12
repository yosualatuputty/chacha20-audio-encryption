import json
from base64 import b64decode
from Crypto.Cipher import ChaCha20

# We assume that the key was somehow securely shared
def decrypt(json_input, key):
    try:
        b64 = json.loads(json_input)
        nonce = b64decode(b64['nonce'])
        ciphertext = b64decode(b64['ciphertext'])
        cipher = ChaCha20.new(key=key, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        print("The message was " + plaintext)
    except (ValueError, KeyError):
        print("Incorrect decryption")
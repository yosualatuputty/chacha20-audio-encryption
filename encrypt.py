import json
from base64 import b64encode
from Crypto.Cipher import ChaCha20
from Crypto.Random import get_random_bytes

def audio_to__byte(audio_file):
    with open(audio_file, 'rb') as f:
        audio_bytes = f.read()
    return audio_bytes
    # <class 'bytes'>   

def encrypt(input='Attack at dawn'):
    plaintext = input.encode('ASCII')
    key = get_random_bytes(32)
    cipher = ChaCha20.new(key=key)
    ciphertext = cipher.encrypt(plaintext)

    nonce = b64encode(cipher.nonce).decode('utf-8')
    ct = b64encode(ciphertext).decode('utf-8')
    key = b64encode(key).decode('utf-8')
    result = json.dumps({'nonce':nonce, 'ciphertext':ct, 'key':key})
    
    return input,result
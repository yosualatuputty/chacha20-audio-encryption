import qrcode
import os

def generate_qr(key, nonce, ext, output_path):
    data = {
        'key': key.hex(),
        'nonce': nonce.hex(),
        'ext': ext
    }
    qr = qrcode.make(str(data))
    qr_path = os.path.join(output_path, 'qr_key.png')
    qr.save(qr_path)
    return qr_path

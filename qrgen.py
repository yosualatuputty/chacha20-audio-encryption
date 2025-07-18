import qrcode

def generate_qr(key, nonce, ext, output_path='/tmp/qr_key_nonce.png'):
    # Gabungkan key dan nonce (hex)
    data = {
        'key': key.hex(),
        'nonce': nonce.hex(),
        'ext': ext
    }

    # Buat QR code
    qr = qrcode.make(str(data))
    qr.save(output_path)
    return output_path

import qrcode
import os

def generate_qr(key, nonce, ext, output_folder='uploads'):
    # Gabungkan key dan nonce (hex)
    data = {
        'key': key.hex(),
        'nonce': nonce.hex(),
        'ext': ext
    }

    # Pastikan foldernya ada
    os.makedirs(output_folder, exist_ok=True)

    # Simpan QR ke dalam folder tersebut
    qr_filename = 'qr_key_nonce.png'
    output_path = os.path.join(output_folder, qr_filename)

    # Buat QR code dan simpan
    qr = qrcode.make(str(data))
    qr.save(output_path)

    return output_path
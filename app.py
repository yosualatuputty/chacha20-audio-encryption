from flask import Flask, request, send_file, jsonify, render_template, redirect,send_from_directory
import os
from werkzeug.utils import secure_filename

from encrypt import encrypt_file
from qrgen import generate_qr
from decrypt import decrypt_file_camera

import signal, sys


qr_code_data = None

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'json', 'txt', 'mp3', 'jpg', 'jpeg', 'pdf', 'mp4',
    'zip', 'tar', 'docx'
}

def handle_exit(sig, frame):
    clear_uploads()
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

@app.route('/client_closed', methods=['POST'])
def client_closed():
    print("[INFO] Tab browser ditutup. Membersihkan folder uploads...")
    clear_uploads()
    return ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_uploads():
    for filename in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f"[WARNING] Failed to delete {file_path}: {e}")

#home page
@app.route('/')
def index():
    clear_uploads()
    return render_template('index.html')


#encrypt page
@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_route():
    clear_uploads()    
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('encrypt.html', error='No file provided')

        file = request.files['file']

        if file.filename == '':
            return render_template('encrypt.html', error='No filename provided')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(input_path)

            # Proses enkripsi
            enc_file, key, nonce, original_ext = encrypt_file(input_path, UPLOAD_FOLDER)
            qr_path = generate_qr(key, nonce, original_ext)

            # Preview plaintext & ciphertext
            with open(input_path, 'rb') as f:
                plaintext_preview = f.read()[:16]

            with open(enc_file, 'rb') as f:
                ciphertext_preview = f.read()[:16]
            
            # Log preview plaintext, ciphertext, key, nonce
            app.logger.info(f"Plaintext Preview: { plaintext_preview}")
            app.logger.info(f"Ciphertext Preview: " + ciphertext_preview.hex())
            app.logger.info(f"Key Preview: "+ key.hex())
            app.logger.info(f"Nonce Preview: "+ nonce.hex())

            return render_template('encrypt.html',
                encrypted_file=os.path.basename(enc_file),
                qr_code_file=os.path.basename(qr_path)
            )

        return render_template('encrypt.html', error='File type not allowed')

    return render_template('encrypt.html')


#decrypt page
@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt():
    decrypted_file = None
    error = None

    if request.method == 'POST':
        try:
            enc_file = request.files.get('encrypted_file')
            qr_file = request.files.get('qr_code_file')
            qr_from_camera = request.form.get('qr_from_camera')
            qr_camera_data = request.form.get('qr_camera_data')

            if not enc_file:
                raise ValueError("Encrypted file is required.")

            enc_filename = os.path.basename(enc_file.filename)
            encrypted_path = os.path.join(UPLOAD_FOLDER, enc_filename)
            enc_file.save(encrypted_path)

            if qr_from_camera == "1" and qr_camera_data:
                output_path = decrypt_file_camera(qr_camera_data, encrypted_path)
            else:
                raise ValueError("QR data not provided.")

            decrypted_file = os.path.basename(output_path)

        except Exception as e:
            error = str(e)

    return render_template("decrypt.html", decrypted_file=decrypted_file, error=error)


#download file
@app.route('/download/<path:filename>')
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'File not found', 404    


if __name__ == '__main__':
    app.run(debug=False)

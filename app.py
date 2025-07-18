from flask import Flask, Response, request, send_file, session, jsonify, render_template, redirect,send_from_directory
import os, uuid, shutil
from werkzeug.utils import secure_filename
from Crypto.Random import get_random_bytes

from encrypt import encrypt_file
from qrgen import generate_qr
from decrypt import decrypt_file_camera

import signal, sys


qr_code_data = None

app = Flask(__name__)
app.secret_key = get_random_bytes(24)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {
    'json', 'txt', 'mp3', 'jpg', 'jpeg', 'pdf', 'mp4',
    'zip', 'tar', 'docx'
}

def get_user_upload_folder():
    if 'user_folder' not in session:
        session['user_folder'] = str(uuid.uuid4())
    folder = os.path.join(UPLOAD_FOLDER, session['user_folder'])
    os.makedirs(folder, exist_ok=True)
    return folder

def handle_exit(sig, frame):
    print("[INFO] Server dimatikan. Menghapus semua uploads global.")
    try:
        shutil.rmtree(UPLOAD_FOLDER)
        print("[INFO] Semua uploads berhasil dihapus.")
    except Exception as e:
        print(f"[WARNING] Gagal menghapus uploads: {e}")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

@app.route('/client_closed', methods=['POST'])
def client_closed():
    print("[INFO] Tab browser ditutup. Membersihkan folder uploads...")
    # session_id = session.pop('user_folder', None)
    clear_uploads(get_user_upload_folder())
    return ''

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_uploads(session_id):
    if session_id is None:
        print("[INFO] Tidak ada folder session yang ditemukan untuk dihapus.")
        return

    folder_path = os.path.join(UPLOAD_FOLDER, session_id)
    if os.path.isdir(folder_path):
        try:
            shutil.rmtree(folder_path)
            print(f"[INFO] Folder session dihapus: {folder_path}")
        except Exception as e:
            print(f"[WARNING] Gagal menghapus folder session: {e}")



#home page
@app.route('/')
def index():
    session_id = session.pop('user_folder', None)
    clear_uploads(session_id)
    return render_template('index.html')


#encrypt page
@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_route():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('encrypt.html', error='No file provided')

        file = request.files['file']

        if file.filename == '':
            return render_template('encrypt.html', error='No filename provided')

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            input_path = os.path.join(get_user_upload_folder(), filename)
            file.save(input_path)

            # Proses enkripsi
            enc_file, key, nonce, original_ext = encrypt_file(input_path, get_user_upload_folder())
            qr_path = generate_qr(key, nonce, original_ext, get_user_upload_folder())

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
    folder = get_user_upload_folder()
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
            encrypted_path = os.path.join(folder, enc_filename)
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
    folder = get_user_upload_folder()
    file_path = os.path.join(folder, filename)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True, download_name=filename)
    return 'File not found', 404   


if __name__ == '__main__':
    app.run(debug=False)

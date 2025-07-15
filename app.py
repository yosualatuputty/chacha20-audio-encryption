from flask import Flask, Response, request, send_file, render_template, session
import os, cv2, uuid, signal, sys, shutil
from werkzeug.utils import secure_filename
from Crypto.Random import get_random_bytes

from encrypt import encrypt_file
from qrgen import generate_qr
from decrypt import decrypt_file, decrypt_file_camera

# Konfigurasi Flask
app = Flask(__name__)
app.secret_key = get_random_bytes(24)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'json', 'txt', 'mp3', 'jpg', 'jpeg', 'pdf', 'mp4', 'zip', 'tar', 'docx'}
qr_code_data = None

# === Manajemen Folder Per-Session ===

def get_user_upload_folder():
    if 'user_folder' not in session:
        session['user_folder'] = str(uuid.uuid4())
    folder = os.path.join(UPLOAD_FOLDER, session['user_folder'])
    os.makedirs(folder, exist_ok=True)
    return folder

def clear_user_uploads():
    folder_id = session.pop('user_folder', None)
    if folder_id:
        folder_path = os.path.join(UPLOAD_FOLDER, folder_id)
        if os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"[INFO] Folder session dihapus: {folder_path}")
            except Exception as e:
                print(f"[WARNING] Gagal menghapus folder session: {e}")

# === Shutdown Handler ===

def handle_exit(sig, frame):
    print("[INFO] Aplikasi dihentikan manual.")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

# === Endpoint: Notifikasi browser ditutup ===

@app.route('/client_closed', methods=['POST'])
def client_closed():
    print("[INFO] Browser client ditutup. Menghapus folder session.")
    clear_user_uploads()
    return '', 204

# === Utilitas ===

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def open_camera(indices=[2, 1, 0]):
    for i in indices:
        cap = cv2.VideoCapture(i)
        if cap and cap.isOpened():
            print(f"[INFO] Menggunakan kamera index {i}")
            return cap
        cap.release()
    raise RuntimeError("Kamera tidak ditemukan.")

# === Video Stream untuk QR ===

def gen_frames():
    camera = open_camera()
    detector = cv2.QRCodeDetector()
    global qr_code_data

    while True:
        success, frame = camera.read()
        if not success:
            continue

        frame = cv2.flip(frame, 1)  # Lakukan flip lebih awal
        data, bbox, _ = detector.detectAndDecode(frame)

        if data and bbox is not None:
            qr_code_data = data
            pts = bbox.astype(int).reshape(-1, 2)

            for i in range(len(pts)):
                pt1 = tuple(pts[i])
                pt2 = tuple(pts[(i + 1) % len(pts)])
                cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

            cv2.putText(frame, "QR Terdeteksi", tuple(pts[0]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            output_path_qr = os.path.join(get_user_upload_folder(), 'image_qr_cv2.png')
            cv2.imwrite('uploads/image_qr_cv2.png', frame)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            break

        # Kalau belum terdeteksi
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    # Jika sudah selesai
    with open('uploads/image_qr_cv2.png', 'rb') as f:
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + f.read() + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# === Routes ===

@app.route('/')
def index():
    clear_user_uploads()
    return render_template('index.html')

@app.route('/encrypt', methods=['GET', 'POST'])
def encrypt_route():
    clear_user_uploads()
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            return render_template('encrypt.html', error='File belum dipilih')

        if allowed_file(file.filename):
            folder = get_user_upload_folder()
            filename = secure_filename(file.filename)
            input_path = os.path.join(folder, filename)
            file.save(input_path)

            enc_file, key, nonce, ext = encrypt_file(input_path, folder)
            qr_path = generate_qr(key, nonce, ext, output_folder=get_user_upload_folder())  # Jika pakai path tetap di qrgen.py

            return render_template('encrypt.html', 
                encrypted_file=os.path.basename(enc_file),
                qr_code_file=os.path.basename(qr_path)
            )
        return render_template('encrypt.html', error='Ekstensi file tidak didukung')
    return render_template('encrypt.html')

@app.route('/decrypt', methods=['GET', 'POST'])
def decrypt_route():
    clear_user_uploads()
    if request.method == 'POST':
        encrypted_file = request.files.get('encrypted_file')
        qr_code_file = request.files.get('qr_code_file')
        qr_from_camera = request.form.get('qr_from_camera') == '1'
        global qr_code_data

        if not encrypted_file:
            return render_template('decrypt.html', error='Encrypted file wajib diunggah.')

        folder = get_user_upload_folder()
        enc_path = os.path.join(folder, secure_filename(encrypted_file.filename))
        encrypted_file.save(enc_path)

        try:
            if qr_from_camera:
                if not qr_code_data:
                    return render_template('decrypt.html', error='QR dari kamera belum terdeteksi.')
                out_path = decrypt_file_camera(qr_code_data, enc_path, folder)
            else:
                if not qr_code_file:
                    return render_template('decrypt.html', error='File QR Code belum diunggah.')

                qr_path = os.path.join(folder, secure_filename(qr_code_file.filename))
                qr_code_file.save(qr_path)
                out_path = decrypt_file(qr_path, enc_path, folder)

            return render_template('decrypt.html', decrypted_file=os.path.basename(out_path))
        except Exception as e:
            return render_template('decrypt.html', error=str(e))

    return render_template('decrypt.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    folder = get_user_upload_folder()
    path = os.path.join(folder, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'File tidak ditemukan', 404

if __name__ == '__main__':
    app.run(debug=True)

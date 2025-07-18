from flask import Flask, Response, request, send_file, jsonify, render_template, redirect,send_from_directory
import os
from werkzeug.utils import secure_filename

from encrypt import encrypt_file
from qrgen import generate_qr
from decrypt import decrypt_file, decrypt_file_camera

import signal, sys


qr_code_data = None

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
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

# def open_camera(indices=[2, 1, 0]):
#     for i in indices:
#         cap = cv2.VideoCapture(i)
#         if cap is not None and cap.isOpened():
#             print(f"[INFO] Using camera at index {i}")
#             return cap
#         cap.release()
#     raise RuntimeError("No available camera found.")

# def gen_frames():
#     camera = open_camera([2, 1, 0])
#     detector = cv2.QRCodeDetector()
#     global qr_code_data

#     while True:
#         success, frame = camera.read()
#         if not success:
#             continue

#         data, bbox, _ = detector.detectAndDecode(frame)
#         if data and bbox is not None:
#             qr_code_data = data
#             app.logger.info(f"QR Detected: {qr_code_data}")

#             # Mirror frame dulu
#             frame = cv2.flip(frame, 1)

#             # Transform koordinat bbox (mirror koordinat X)
#             frame_width = frame.shape[1]
#             pts = bbox.astype(int).reshape(-1, 2)
#             mirrored_pts = []
#             for (x, y) in pts:
#                 mirrored_pts.append((frame_width - x, y))

#             # Gambar kotak QR (mirror)
#             for i in range(len(mirrored_pts)):
#                 pt1 = mirrored_pts[i]
#                 pt2 = mirrored_pts[(i + 1) % len(mirrored_pts)]
#                 cv2.line(frame, pt1, pt2, (0, 255, 0), 2)

#             # Teks di atas QR
#             text_x, text_y = mirrored_pts[0]
#             cv2.putText(frame, "QR Terdeteksi", (text_x, text_y - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_AA)

#             # Simpan hasil frame
#             cv2.imwrite('uploads/image_qr_cv2.png', frame)

#             # Encode untuk streaming
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#             break

#         else:
#             # Belum terdeteksi: tampilkan frame biasa (mirror)
#             try:
#                 frame = cv2.flip(frame, 1)
#                 ret, buffer = cv2.imencode('.jpg', frame)
#                 frame = buffer.tobytes()
#                 yield (b'--frame\r\n'
#                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#             except Exception as e:
#                 print(f"[ERROR] Encoding frame: {e}")
#                 continue

#     # Fallback: tampilkan gambar hasil terakhir
#     with open('uploads/image_qr_cv2.png', 'rb') as f:
#         frame = f.read()
#     yield (b'--frame\r\n'
#            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        
# @app.route('/video_feed')
# def video_feed():
#     return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

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

#decrypt camera
# @app.route('/decrypt/camera')
# def render_video():
#     return render_template('decrypt.html', camera=True)

# @app.route('/process_video', methods=['GET', 'POST'])
# def process_video():
#     clear_uploads()
#     global qr_code_data
#     encrypted_file = request.files.get('encrypted_file')
#     if not encrypted_file:
#         return render_template('decrypt.html', error='Please upload encrypted file')
#     if not qr_code_data:
#         return render_template('decrypt.html', error='No QR detected!')
#     enc_filename = secure_filename(encrypted_file.filename)

#     enc_path = os.path.join(UPLOAD_FOLDER, enc_filename)
#     encrypted_file.save(enc_path)

#     try:
#         output_path = decrypt_file_camera(qr_code_data, enc_path, UPLOAD_FOLDER)
#         return render_template('decrypt.html', decrypted_file=os.path.basename(output_path))
#     except Exception as e:
#         return render_template('decrypt.html', error=str(e))


#download file
@app.route('/download/<path:filename>')
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'File not found', 404    


if __name__ == '__main__':
    app.run(debug=False)

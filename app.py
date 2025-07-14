from flask import Flask, Response, request, send_file, jsonify, render_template, redirect,send_from_directory
import os, cv2
from werkzeug.utils import secure_filename

from encrypt import encrypt_file
from qrgen import generate_qr
from decrypt import decrypt_file, decrypt_file_camera

qr_code_data = None

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'json', 'txt', 'mp3', 'jpg', 'jpeg', 'pdf', 'mp4'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# gambar dari kamera
def gen_frames():  # generate frame by frame from camera
    camera = cv2.VideoCapture(2)
    detector = cv2.QRCodeDetector()
    global qr_code_data
    while True:
        success, frame = camera.read() 
        if success:
            data, bbox, _ = detector.detectAndDecode(frame)
            # check if there is a QRCode in the image
            if data:
                qr_code_data = data
                app.logger.info(f"QR Detected: {qr_code_data}")
                break
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            except Exception as e:
                pass
                
        else:
            pass
    with open('static/image.png', 'rb') as f:
        frame = f.read()
    yield (b'--frame\r\n'
    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
        
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

#home page
@app.route('/')
def index():
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
def decrypt_route():
    if request.method == 'POST':
        encrypted_file = request.files.get('encrypted_file')
        qr_code_file = request.files.get('qr_code_file')

        if not encrypted_file or not qr_code_file:
            return render_template('decrypt.html', error='Both files are required.')

        enc_filename = secure_filename(encrypted_file.filename)
        qr_filename = secure_filename(qr_code_file.filename)

        enc_path = os.path.join(UPLOAD_FOLDER, enc_filename)
        qr_path = os.path.join(UPLOAD_FOLDER, qr_filename)

        encrypted_file.save(enc_path)
        qr_code_file.save(qr_path)

        try:
            output_path = decrypt_file(qr_path, enc_path, UPLOAD_FOLDER)
            return render_template('decrypt.html', decrypted_file=os.path.basename(output_path))
        except Exception as e:
            return render_template('decrypt.html', error=str(e))

    return render_template('decrypt.html')

#decrypt camera
@app.route('/decrypt/camera')
def render_video():
    return render_template('decrypt.html', camera=True)

@app.route('/process_video', methods=['GET', 'POST'])
def process_video():
    global qr_code_data
    encrypted_file = request.files.get('encrypted_file')
    if not encrypted_file:
        return render_template('decrypt.html', error='Please upload encrypted file')
    if not qr_code_data:
        return render_template('decrypt.html', error='No QR detected!')
    enc_filename = secure_filename(encrypted_file.filename)

    enc_path = os.path.join(UPLOAD_FOLDER, enc_filename)
    encrypted_file.save(enc_path)

    try:
        output_path = decrypt_file_camera(qr_code_data, enc_path, UPLOAD_FOLDER)
        return render_template('decrypt.html', decrypted_file=os.path.basename(output_path))
    except Exception as e:
        return render_template('decrypt.html', error=str(e))


#download file
@app.route('/download/<path:filename>')
def download_file(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return 'File not found', 404    


if __name__ == '__main__':
    app.run(debug=True)

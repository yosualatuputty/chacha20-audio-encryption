from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from encrypt import encrypt
import json

app = Flask(__name__)
bootstrap = Bootstrap(app)

#index
@app.route('/')
def index():
    return render_template('index.html')

#encrypt page
@app.route('/encrypt')
def encrypt_view():
    plaintext, json_result = encrypt()
    json_result = json.loads(json_result)
    return render_template('encrypt.html', plaintext=plaintext, ciphertext=json_result['ciphertext'])

#decrypt page
@app.route('/decrypt')
def decrypt_view():
    return render_template('decrypt.html')

#main
if __name__ == "__main__":
    app.run(debug=True)
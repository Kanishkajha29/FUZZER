from flask import Flask, render_template, request, redirect, url_for
import os
from utils.vhost import VHostEnum

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start_enum', methods=['POST'])
def start_enum():
    target_website = request.form['target_website']
    payload_option = request.form['payload_option']
    
    if payload_option == 'custom' and 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            payload_file = filename
        else:
            return "Invalid file format", 400
    else:
        payload_file = './default_wordlists/vhost.txt'
    
    vhost_enum = VHostEnum(target_website, payload_file)
    result = vhost_enum.run_enum()
    
    return render_template('results.html', target=target_website, result=result)

if __name__ == '__main__':
    app.run(debug=True)

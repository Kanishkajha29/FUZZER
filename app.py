from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from utils.xss import test_xss

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_PAYLOAD_FILE = 'default_wordlist/xss.txt'

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        endpoint = request.form.get('endpoint')
        payload_choice = request.form.get('payload_choice')

        if not endpoint:
            flash('Please enter a target website endpoint.', 'error')
            return redirect(url_for('index'))

        if payload_choice == 'custom':
            file = request.files.get('payload_file')
            if not file or file.filename == '':
                flash('Please upload a payload file.', 'error')
                return redirect(url_for('index'))

            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        else:
            file_path = DEFAULT_PAYLOAD_FILE

        results = test_xss(endpoint, file_path)
        return render_template('results.html', results=results, endpoint=endpoint)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

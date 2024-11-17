from flask import Flask, render_template, request, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from utils.sql import perform_sql_injection_test


app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'
DEFAULT_PAYLOAD_PATH = 'default_wordlist/sql.txt'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        endpoint = request.form['endpoint']
        payload_choice = request.form['payload']
        if payload_choice == 'default':
            payload_path = DEFAULT_PAYLOAD_PATH
        elif payload_choice == 'custom':
            file = request.files['custom_payload']
            if file and file.filename:
                filename = secure_filename(file.filename)
                payload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(payload_path)
            else:
                flash('No file uploaded. Please upload a valid file.')
                return redirect(url_for('index'))
        else:
            flash('Invalid payload choice.')
            return redirect(url_for('index'))

        results = perform_sql_injection_test(endpoint, payload_path)
        return render_template('results.html', endpoint=endpoint, results=results)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

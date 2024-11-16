from flask import Flask, render_template, request, redirect, url_for, flash
import os
import concurrent.futures
import requests
from utils.subdomain_fuzz import subdomain_fuzzing

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SECRET_KEY'] = 'your_secret_key'

# Ensure the uploads folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        target_url = request.form['target_url']
        payload_option = request.form['payload_option']

        if not target_url:
            flash("Target URL is required!", 'danger')
            return redirect(url_for('index'))

        if payload_option == 'custom' and 'custom_payload' in request.files:
            custom_payload = request.files['custom_payload']
            if custom_payload.filename != '':
                # Save the custom payload file
                payload_path = os.path.join(app.config['UPLOAD_FOLDER'], custom_payload.filename)
                custom_payload.save(payload_path)
            else:
                flash("No file selected for custom payload.", 'danger')
                return redirect(url_for('index'))
        else:
            payload_path = 'default_wordlists/subdomain.txt'

        try:
            subdomains = subdomain_fuzzing(target_url, payload_path)
            if not subdomains:
                flash("No subdomains found.", 'warning')
            return render_template('results.html', target_url=target_url, subdomains=subdomains)
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'danger')
            return redirect(url_for('index'))

    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)

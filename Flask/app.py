from flask import Flask, render_template, request, flash, redirect, url_for
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from utils.dir_fuzz import dir_fuzz  # Custom module for directory fuzzing
from utils.subdomain_fuzz import subdomain_fuzzing  # Custom module for subdomain fuzzing

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, unique key for production use

# Create required directories if they don't exist
os.makedirs('uploads', exist_ok=True)
os.makedirs('default_wordlists', exist_ok=True)

# Function to detect API endpoints
def detect_api_endpoints(target_url, payloads):
    if not payloads:
        # Use the default wordlist if no payload is provided
        wordlist_path = os.path.join('default_wordlists', 'api.txt')
        with open(wordlist_path, 'r') as file:
            payloads = file.read().splitlines()

    results = []

    # Helper function to test a single URL
    def test_url(payload):
        url_to_test = f"https://{target_url}/{payload}"
        try:
            response = requests.get(url_to_test, timeout=5)
            if response.status_code == 200:
                return f"Endpoint found: {url_to_test} - Status: {response.status_code}"
        except requests.exceptions.RequestException:
            pass
        return None

    # Parallelize requests using ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=10) as executor:
        results.extend(executor.map(test_url, payloads))

    return [result for result in results if result]

# Default route for the application
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle fuzzing operations
@app.route('/fuzz', methods=['POST'])
def fuzz():
    target_url = request.form['target_url']
    if not target_url:
        flash("Target URL is required!", 'danger')
        return redirect(url_for('index'))

    results = {}

    # Directory fuzzing logic
    if request.form.get('directory_fuzz') == 'yes':
        wordlist_choice = request.form['wordlist']
        if wordlist_choice == 'custom':
            wordlist = request.files['wordlist_file']
            if wordlist:
                wordlist_path = os.path.join('uploads', wordlist.filename)
                wordlist.save(wordlist_path)
            else:
                flash("Please upload a wordlist file for directory fuzzing.", 'danger')
                return redirect(url_for('index'))
        else:
            wordlist_path = os.path.join('default_wordlists', 'directory.txt')

        try:
            fuzz_results = dir_fuzz(target_url, wordlist_path)
            results['directory'] = fuzz_results
        except Exception as e:
            flash(f"An error occurred during directory fuzzing: {str(e)}", 'danger')
            return redirect(url_for('index'))

    # Subdomain fuzzing logic
    if request.form.get('subdomain_fuzz') == 'yes':
        payload_option = request.form['payload_option']
        if payload_option == 'custom':
            custom_payload = request.files['custom_payload']
            if custom_payload and custom_payload.filename != '':
                payload_path = os.path.join('uploads', custom_payload.filename)
                custom_payload.save(payload_path)
            else:
                flash("No file selected for custom payload.", 'danger')
                return redirect(url_for('index'))
        else:
            payload_path = os.path.join('default_wordlists', 'subdomain.txt')

        try:
            subdomains = subdomain_fuzzing(target_url, payload_path)
            if subdomains:
                results['subdomain'] = subdomains
            else:
                flash("No subdomains found.", 'warning')
        except Exception as e:
            flash(f"An error occurred during subdomain fuzzing: {str(e)}", 'danger')
            return redirect(url_for('index'))

    # Ensure at least one result exists
    if not results:
        flash("Please select at least one fuzzing option.", 'danger')
        return redirect(url_for('index'))

    return render_template('results.html', target_url=target_url, results=results)

# Route to detect API endpoints
@app.route('/detect', methods=['POST'])
def detect():
    target_url = request.form['target_url']
    payload_choice = request.form['payload_choice']
    custom_file = request.files.get('custom_file')

    payloads = []
    if payload_choice == 'custom' and custom_file:
        payloads = custom_file.read().decode('utf-8').splitlines()
    else:
        wordlist_path = os.path.join('default_wordlists', 'api.txt')
        with open(wordlist_path, 'r') as file:
            payloads = file.read().splitlines()

    results = detect_api_endpoints(target_url, payloads)
    if not results:
        return render_template('results.html', message="No successful endpoints found.")
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)

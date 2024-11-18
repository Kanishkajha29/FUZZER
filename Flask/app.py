from flask import Flask, render_template, request, redirect, url_for, flash
import os
import requests
from concurrent.futures import ThreadPoolExecutor
from werkzeug.utils import secure_filename
from utils.dir_fuzz import dir_fuzz  # Custom module for directory fuzzing
from utils.subdomain_fuzz import subdomain_fuzzing  # Custom module for subdomain fuzzing
from utils.vhost import VHostEnum  # Custom module for VHost enumeration
from utils.sql import perform_sql_injection_test  # Custom module for SQL injection tests
from utils.rate_limit import perform_rate_limit_test, format_url  # Custom module for rate limit testing
from utils.info_gathr import get_network_map, get_whois_info, get_ssl_info  # Custom modules for information gathering


app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong, unique key for production
UPLOAD_FOLDER = './uploads'
DEFAULT_WORDLIST_PATH = './default_wordlists'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'txt'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DEFAULT_WORDLIST_PATH, exist_ok=True)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Function to detect API endpoints
def detect_api_endpoints(target_url, payloads):
    if not payloads:
        wordlist_path = os.path.join(DEFAULT_WORDLIST_PATH, 'api.txt')
        with open(wordlist_path, 'r') as file:
            payloads = file.read().splitlines()

    results = []

    def test_url(payload):
        url_to_test = f"https://{target_url}/{payload}"
        try:
            response = requests.get(url_to_test, timeout=5)
            if response.status_code == 200:
                return f"Endpoint found: {url_to_test} - Status: {response.status_code}"
        except requests.exceptions.RequestException:
            pass
        return None

    with ThreadPoolExecutor(max_workers=10) as executor:
        results.extend(executor.map(test_url, payloads))

    return [result for result in results if result]

# Function to test for XSS vulnerabilities
def test_xss(endpoint, payload_file):
    results = []
    try:
        with open(payload_file, 'r') as file:
            payloads = file.readlines()

        for payload in payloads:
            payload = payload.strip()
            response = requests.get(f"{endpoint}?q={payload}")
            if payload in response.text:
                results.append({
                    'payload': payload,
                    'status': 'Vulnerable',
                    'details': 'Payload reflected in the response'
                })
            else:
                results.append({
                    'payload': payload,
                    'status': 'Safe',
                    'details': 'No reflection of payload in the response'
                })
    except Exception as e:
        results.append({'error': str(e)})

    return results

@app.route('/')
def index():
    return render_template('index.html')

# Route for fuzzing and vulnerability testing (from Code 1)
@app.route('/fuzz', methods=['POST'])
def fuzz():
    target_url = request.form['target_url']
    if not target_url:
        flash("Target URL is required!", 'danger')
        return redirect(url_for('index'))

    results = {}

    if request.form.get('directory_fuzz') == 'yes':
        wordlist_choice = request.form['wordlist']
        if wordlist_choice == 'custom':
            wordlist = request.files['wordlist_file']
            if wordlist and allowed_file(wordlist.filename):
                wordlist_path = os.path.join(UPLOAD_FOLDER, secure_filename(wordlist.filename))
                wordlist.save(wordlist_path)
            else:
                flash("Please upload a valid wordlist file.", 'danger')
                return redirect(url_for('index'))
        else:
            wordlist_path = os.path.join(DEFAULT_WORDLIST_PATH, 'directory.txt')

        try:
            fuzz_results = dir_fuzz(target_url, wordlist_path)
            results['directory'] = fuzz_results
        except Exception as e:
            flash(f"An error occurred during directory fuzzing: {str(e)}", 'danger')
            return redirect(url_for('index'))

    if request.form.get('subdomain_fuzz') == 'yes':
        payload_option = request.form['payload_option']
        if payload_option == 'custom':
            custom_payload = request.files['custom_payload']
            if custom_payload and allowed_file(custom_payload.filename):
                payload_path = os.path.join(UPLOAD_FOLDER, secure_filename(custom_payload.filename))
                custom_payload.save(payload_path)
            else:
                flash("Please upload a valid custom payload file.", 'danger')
                return redirect(url_for('index'))
        else:
            payload_path = os.path.join(DEFAULT_WORDLIST_PATH, 'subdomain.txt')

        try:
            subdomains = subdomain_fuzzing(target_url, payload_path)
            if subdomains:
                results['subdomain'] = subdomains
            else:
                flash("No subdomains found.", 'warning')
        except Exception as e:
            flash(f"An error occurred during subdomain fuzzing: {str(e)}", 'danger')
            return redirect(url_for('index'))

    if not results:
        flash("Please select at least one fuzzing option.", 'danger')
        return redirect(url_for('index'))

    return render_template('results.html', target_url=target_url, results=results)

# Route for XSS testing (from Code 1)
@app.route('/xss_test', methods=['POST'])
def xss_test():
    endpoint = request.form['endpoint']
    payload_choice = request.form['payload']
    
    if payload_choice == 'default':
        payload_path = os.path.join(DEFAULT_WORDLIST_PATH, 'xss.txt')
    elif payload_choice == 'custom':
        file = request.files['custom_payload']
        if file and allowed_file(file.filename):
            filename = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            file.save(filename)
            payload_path = filename
        else:
            flash("Invalid file uploaded. Please upload a valid file.", 'danger')
            return redirect(url_for('index'))
    else:
        flash("Invalid payload choice.", 'danger')
        return redirect(url_for('index'))

    results = test_xss(endpoint, payload_path)
    return render_template('results.html', endpoint=endpoint, results=results)

# Route for VHost enumeration (from Code 1)
@app.route('/start_enum', methods=['POST'])
def start_enum():
    target_website = request.form['target_website']
    payload_option = request.form['payload_option']

    if payload_option == 'custom' and 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
            file.save(filename)
            payload_file = filename
        else:
            return "Invalid file format", 400
    else:
        payload_file = os.path.join(DEFAULT_WORDLIST_PATH, 'vhost.txt')

    vhost_enum = VHostEnum(target_website, payload_file)
    result = vhost_enum.run_enum()

    return render_template('results.html', target=target_website, result=result)

# Route for SQL Injection testing (from Code 1)
@app.route('/sql_test', methods=['POST'])
def sql_test():
    endpoint = request.form['endpoint']
    payload_choice = request.form['payload']
    if payload_choice == 'default':
        payload_path = os.path.join(DEFAULT_WORDLIST_PATH, 'sql.txt')
    elif payload_choice == 'custom':
        file = request.files['custom_payload']
        if file and allowed_file(file.filename):
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

# Route for Rate Limit testing (from Code 1)
@app.route('/rate_limit_test', methods=['POST'])
def rate_limit_test():
    target_url = request.form.get('target_url')
    num_requests = request.form.get('num_requests', type=int)
    
    if not target_url or not num_requests or num_requests <= 0:
        flash("Please enter a valid target endpoint and a positive number of requests.", 'danger')
        return redirect(url_for('index'))

    # Format URL to ensure it is valid
    formatted_url = format_url(target_url)

    # Perform rate limit testing
    results = perform_rate_limit_test(formatted_url, num_requests)
    return render_template('results.html', results=results, num_requests=num_requests)

# Route for Information Gathering (from Code 2)
@app.route('/info_gather', methods=['POST'])
def info_gather():
    url = request.form.get('target_url')
    options = {
        "network_map": request.form.get('network_map') == 'yes',
        "whois_info": request.form.get('whois_info') == 'yes',
        "ssl_info": request.form.get('ssl_info') == 'yes'
    }
    results = {}

    if options['network_map']:
        results['network_map'] = get_network_map(url)

    if options['whois_info']:
        results['whois_info'] = get_whois_info(url)

    if options['ssl_info']:
        results['ssl_info'] = get_ssl_info(url)

    return render_template('result.html', url=url, results=results)

if __name__ == '__main__':
    app.run(debug=True)

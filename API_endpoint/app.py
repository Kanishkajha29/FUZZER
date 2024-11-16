from flask import Flask, render_template, request
import os
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# Function to detect API endpoints (same as in api.py)
def detect_api_endpoints(target_url, payloads, use_custom=False):
    if not payloads:
        # If no custom payload, use the default wordlist (api.txt)
        wordlist_path = os.path.join('default_wordlists', 'api.txt')
        with open(wordlist_path, 'r') as file:
            payloads = file.read().splitlines()

    results = []

    # Define a helper function to test a single URL
    def test_url(payload):
        url_to_test = f"https://{target_url}/{payload}"
        try:
            # Send a GET request to the endpoint and check for a successful response
            response = requests.get(url_to_test, timeout=5)
            if response.status_code == 200:
                return f"Endpoint found: {url_to_test} - Status: {response.status_code}"
            else:
                return None  # Do not return any result for non-200 responses
        except requests.exceptions.RequestException as e:
            return None  # Do not return any result for errors

    # Use ThreadPoolExecutor to parallelize requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Map the payloads to the test_url function and collect the results
        results.extend(executor.map(test_url, payloads))

    # Filter out None values (i.e., unsuccessful tests)
    return [result for result in results if result is not None]

# Route for the homepage (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Route for detecting API endpoints and rendering results (result.html)
@app.route('/detect', methods=['POST'])
def detect():
    target_url = request.form['target_url']
    payload_choice = request.form['payload_choice']
    custom_file = request.files.get('custom_file')

    payloads = []

    if payload_choice == 'custom' and custom_file:
        # Read the custom payload file
        payloads = custom_file.read().decode('utf-8').splitlines()
    else:
        # Use the default wordlist
        wordlist_path = os.path.join('default_wordlists', 'api.txt')
        with open(wordlist_path, 'r') as file:
            payloads = file.read().splitlines()

    results = detect_api_endpoints(target_url, payloads)
    if not results:
        return render_template('results.html', message="No successful endpoints found.")
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False)

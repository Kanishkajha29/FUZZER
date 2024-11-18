import requests
import os
from concurrent.futures import ThreadPoolExecutor

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
                return f"Tested: {url_to_test} - Status: {response.status_code}"
        except requests.exceptions.RequestException as e:
            return f"Error testing {url_to_test}: {str(e)}"

    # Use ThreadPoolExecutor to parallelize requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Map the payloads to the test_url function and collect the results
        results.extend(executor.map(test_url, payloads))

    return results
import requests

def perform_sql_injection_test(endpoint, payload_path):
    results = []
    try:
        with open(payload_path, 'r') as payload_file:
            payloads = payload_file.readlines()
        
        # Get the baseline response for comparison
        baseline_response = requests.get(endpoint)
        baseline_content = baseline_response.text.strip()

        for payload in payloads:
            payload = payload.strip()
            test_url = f'{endpoint}{payload}'
            response = requests.get(test_url)

            is_anomalous = response.text.strip() != baseline_content
            if is_anomalous:  # Only add to results if it's anomalous
                results.append({
                    'payload': payload,
                    'status_code': response.status_code,
                    'response_snippet': response.text[:100],
                    'anomalous': is_anomalous
                })
    except Exception as e:
        results.append({'error': str(e)})
    return results

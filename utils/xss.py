import requests

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

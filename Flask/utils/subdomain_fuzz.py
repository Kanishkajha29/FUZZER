import requests
import concurrent.futures

def subdomain_fuzzing(target_url, wordlist_path):
    subdomains = []
    
    try:
        with open(wordlist_path, 'r') as wordlist:
            subdomain_list = [line.strip() for line in wordlist if line.strip()]
        
        # Using ThreadPoolExecutor to speed up requests by handling them concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_subdomain = {
                executor.submit(check_subdomain, subdomain, target_url): subdomain
                for subdomain in subdomain_list
            }
            
            for future in concurrent.futures.as_completed(future_to_subdomain):
                subdomain = future_to_subdomain[future]
                try:
                    if future.result():
                        subdomains.append(f'http://{subdomain}.{target_url}')
                except Exception as exc:
                    print(f'Subdomain {subdomain} generated an exception: {exc}')
                
    except FileNotFoundError:
        raise Exception(f"Wordlist file not found at {wordlist_path}")
    except Exception as e:
        raise Exception(f"An error occurred during fuzzing: {str(e)}")
    
    return subdomains

def check_subdomain(subdomain, target_url):
    url = f'http://{subdomain}.{target_url}'
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return True
    except requests.RequestException:
        return False
    return False

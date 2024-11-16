import requests
from concurrent.futures import ThreadPoolExecutor

def dir_fuzz(target_url, wordlist_path="default_wordlists/directory.txt", max_threads=10):
    found_urls = []  # List to store found URLs
    
    def test_directory(directory):
        url = f"http://{target_url}/{directory.strip()}"
        try:
            with requests.Session() as session:
                response = session.get(url, timeout=3)
                if response.status_code == 200:
                    found_urls.append(f"[FOUND] {url} - Status Code: {response.status_code}")
                elif response.status_code == 403:
                    found_urls.append(f"[FORBIDDEN] {url} - Status Code: {response.status_code}")
        except requests.RequestException as e:
            found_urls.append(f"[ERROR] Could not connect to {url}: {e}")

    try:
        with open(wordlist_path, "r") as wordlist:
            directories = wordlist.readlines()
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            executor.map(test_directory, directories)

    except FileNotFoundError:
        found_urls.append(f"Error: Wordlist file '{wordlist_path}' not found.")
    
    return found_urls  # Return the list of found URLs

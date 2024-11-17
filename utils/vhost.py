import requests

class VHostEnum:
    def __init__(self, target, payload_file):
        self.target = target
        self.payload_file = payload_file
    
    def load_payloads(self):
        with open(self.payload_file, 'r') as file:
            return [line.strip() for line in file.readlines()]
    
    def run_enum(self):
        payloads = self.load_payloads()
        found_vhosts = []
        
        for payload in payloads:
            url = f"http://{payload}.{self.target}"
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    found_vhosts.append(url)
            except requests.RequestException:
                continue
        
        return found_vhosts

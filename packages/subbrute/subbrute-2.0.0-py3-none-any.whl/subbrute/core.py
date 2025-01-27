import socket

def scan(domain, wordlist, callback=None):
    results = []
    for sub in wordlist:
        try:
            full_domain = f"{sub}.{domain}"
            ip = socket.gethostbyname(full_domain)
            result = (full_domain, ip, "valid")
        except socket.gaierror:
            result = (f"{sub}.{domain}", None, "invalid")
        
        results.append(result)
        
        if callback:
            callback(*result)
    
    return results

def load(file_path):
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

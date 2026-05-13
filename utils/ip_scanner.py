import socket
import requests

class IPScanner:
    def __init__(self):
        pass

    def scan_network(self):
        scanned_data = []
        local_ip = socket.gethostbyname(socket.gethostname())

        # Example: Fetch details of the local machine
        ip_details = self.get_ip_details(local_ip)
        scanned_data.append({"ip": local_ip, "details": ip_details})

        return scanned_data

    def get_ip_details(self, ip):
        try:
            response = requests.get(f"https://ipinfo.io/{ip}/json")
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
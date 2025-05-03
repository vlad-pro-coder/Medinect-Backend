import requests
from bs4 import BeautifulSoup

url = 'https://www.paulsmarteurope.com/acid-reflux-digestive/'  # Replace with your target URL
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': '*/*',
    'Connection': 'keep-alive',
}

# Sending the request
try:
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup.findAll('article',class_="product-box"))
    else:
        print(f"Failed to ping {url}. Status code: {response.status_code}")
except requests.RequestException as e:
    print(f"Error: {e}")

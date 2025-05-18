import sys
import requests
from bs4 import BeautifulSoup
import GlobalVariables
import Trie
import aiohttp
import asyncio

url = 'https://www.crinfarm.ro/vitamine-si-suplimente'  # Replace with your target URL
domain = 'https://www.crinfarm.ro/'
headers = {#the headers for a successful conection
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
        }

async def fetch(session):  # Ensure 'url' is passed as a parameter
    try:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Error {response.status}: {url}")  # Properly checks 'response.status'
                sys.exit(1)
    except aiohttp.ClientError as e:
        print(f"Failed to fetch {url}: {e}")  # Handles ClientError correctly
        sys.exit(1)

# Sending the request
async def main():
    try:
        words = Trie.Trie(["calciu"])
        resultedData = []
        async with aiohttp.ClientSession(headers=headers) as session:
            response = await fetch(session)
            soup = BeautifulSoup(response, 'html.parser')
            GlobalVariables.crin_farm_scraper(soup,domain,resultedData,words)
            print(resultedData)
    except requests.RequestException as e:
        print(f"Error: {e}")

asyncio.run(main())

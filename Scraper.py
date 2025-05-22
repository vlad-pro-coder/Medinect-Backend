from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import asyncio
import aiohttp
import GlobalVariables
import Trie

class Scraper:
    def __init__(self,userUID,wordsRequested,language):
        self.visited_urls = set()#to not go on the same links twice
        self.allowedDomain = ""#the allowed domain to not wonder off to facebook for example
        self.lock = asyncio.Lock()#asyncio lock
        self.ScrapedData = []#this will be given to the user after the scrape is done
        self.TrieWords = Trie.Trie(wordsRequested)#the trie instance
        #note that we dont need a thread lock for these 2 start_urls and scrapping_rules because they are constants and never changed
        self.start_urls = GlobalVariables.scrapeSites[language]#the urls to scan
        self.scraping_rules = GlobalVariables.scrapeRules[language]#the rules for the scan
        self.userUID = userUID#the user UID
        self.language = language#the language
        self.headers = {#the headers for a successful conection
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
        }

    def get_scraper(self,url):#this function gives back the scraper rules and the site to scrape
        for site, scraper in self.scraping_rules.items(): 
            if site in url: 
                return scraper, site
        return None

    #functions
        

    async def fetch(self,session,url):
        try: #this fetches the html content of a page
            async with session.get(url) as response: 
                if response.status == 200: 
                    return await response.text() 
                else: 
                    print(f"Error {response.status}: {url}") #error while doing that
                    return None 
        except aiohttp.ClientError as e: 
            print(f"Failed to fetch {url}: {e}") #failed to connect
            return None

    async def is_valid_url(self,url):
        parsed = urlparse(url)#if the url has "https://" and a valid domain name
        return bool(parsed.netloc) and bool(parsed.scheme)

    def has_exception(self,url): #if the url containes any of these exceptions the url is trashed
        if "order=" in url:
            return True
        if "id_currency" in url:
            return True
        if self.language == "fra":
            if "fr" not in url:
                return True
            return bool(re.search(r'\d',url))
        if self.language == "deu":
            if "?" in url:
                return True
            if "brands" in url:
                return True
            return bool(re.search(r'\d',url))
        if self.language == "eng":
            if "prd-" in url:
                return True
            if "brand=" in url:
                return True
            if "/brands" in url:
                return True
            if "/offer" in url:
                return True
            if "brandname=" in url:
                return True
            if "promo=" in url:
                return True
            if "stock=" in url:
                return True
            if "price=" in url:
                return True
            if "rating=" in url:
                return True
        if self.language == "ron":
            if "sort_by" in url:
                return True
            if "info-tei" in url:
                return True
            if "#" in url:
                return True
            if "marci" in url:
                return True
            if "magazine" in url:
                return True
            if "articole" in url:
                return True
            if "page=" in url:
                return True
            if "blog" in url:
                return True
            if "legal" in url:
                return True
            if "brand" in url:
                return True
            if "gama" in url:
                return True
            if "cauti" in url:
                return True
            if "pag-" in url:
                return False
            return bool(re.search(r'\d',url))
        return False
    
    async def create_page_links(self,session,url):
        try:
            available_pages = []
            page = 2
            domain_name = urlparse(url).netloc
            if domain_name not in GlobalVariables.available_pages_domains:
                return []
            while True:
                link_url = url + GlobalVariables.available_pages_domains[domain_name] + str(page)
                
                async with aiohttp.ClientSession(headers=self.headers) as session:
                    async with session.head(link_url, allow_redirects=True) as response:
                        if 200 <= response.status < 400:
                            tempsoup = BeautifulSoup(await response.text(), 'html.parser')
                            if tempsoup.find('div',class_="notice alert") != None:
                                available_pages.append(link_url)
                            else:
                                return available_pages
                        else:
                                return available_pages
                page+=1
        except aiohttp.ClientError as e: 
            print("error",e)

    async def crawl(self,session,url):
        
        async with self.lock: #with the lock we check if the url we are scraping is in the visited urls
            if url in self.visited_urls: 
                return 
            self.visited_urls.add(url)
        print(f"Crawling: {url}")

        try:
            html_content = await self.fetch(session,url)#get the html content
            if not html_content: #if error then do nothing
                return
            soup = BeautifulSoup(html_content, 'html.parser')#give it to the bs4 library
            # Extract and process data from the page
            process_page,domain = self.get_scraper(url)#get the domain and the scrape rules
            process_page(soup,domain,self.ScrapedData,self.TrieWords)#process the resulted html

            # Find and follow links on the page
            tasks = []

            
            for link in await self.create_page_links(session,url):
                if await self.is_valid_url(link):
                    task = asyncio.create_task(self.crawl(session,link_url))
                    tasks.append(task)

            for link in soup.find_all('a', href=True):
                if not self.has_exception(link['href']):
                    link_url = urljoin(domain, link['href'])
                    if await self.is_valid_url(link_url):#after every checking if the link is correct then we put it in a task scheduler
                        task = asyncio.create_task(self.crawl(session,link_url))
                        tasks.append(task)
            await asyncio.gather(*tasks)#this runs every task all at once for better performance async I/O
        except Exception as e:
            print(f"Failed to crawl {url}: {e}")#error


    async def main(self,start_urls):
        async with aiohttp.ClientSession(headers=self.headers) as session:#begin a session with link pooling
            for index,start_url in enumerate(start_urls):
                global allowedDomain
                allowedDomain = start_url
                await self.crawl(session,start_url)#take every url and crawl through it maybe all also use a scheduler here in the future
                with GlobalVariables.threadLock:#calculate how much we have done until now
                    GlobalVariables.procentageReadySraper[self.userUID] = (index + 1) / len(start_urls) * 100

    # Start crawling
    def start_scraper(self):#starts scraper
        asyncio.run(self.main(self.start_urls))#runs the scraper
        with GlobalVariables.threadLock:#after the scraper is done we append the results 
            GlobalVariables.ResultsScraper[self.userUID] = self.ScrapedData

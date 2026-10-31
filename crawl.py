from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import asyncio
import aiohttp

class AsyncCrawler:
    def __init__(self, base_url): 
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.max_concurrency = 10
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if normalized_url in self.visited:
                return False
            else:
                self.visited.add(normalized_url)
                return True
    
    async def get_html(self, url: str):
        try:
            async with self.session.get(url, headers={"User-Agent": "SomeCrawlerName/1.0"}) as response:
                if response.status > 399:
                    print(f"got HTTP error: {response.status}")
                    return None

                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(f"got non-HTML response: {content_type}")
                    return None

                return await response.text()
        except Exception as e:
            print(f"network error while fetching {url}: {e}")
            return None
        
    async def crawl_page(self, current_url: str):
        current_url_obj = urlsplit(current_url)
        if current_url_obj.netloc != self.base_domain:
            return

        normalized_url = normalize_url(current_url)
        is_new = await self.add_page_visit(normalized_url)
        if not is_new:
            return
        async with self.semaphore:
            html = await self.get_html(current_url)
            if html is None:
                return
            page_info = extract_page_data(html, current_url)
            async with self.lock:
                self.page_data[normalized_url] = page_info
        next_urls = page_info["outgoing_links"]
        tasks = []
        for next_url in next_urls:
            tasks.append(asyncio.create_task(self.crawl_page(next_url)))
        if tasks:
            await asyncio.gather(*tasks)

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return self.page_data


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

def normalize_url(raw_url: str) -> str:
    lower = raw_url.lower()
    parsed = urlsplit(lower)
    netloc = parsed.netloc
    path = parsed.path.rstrip("/")
    return netloc + path

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    if h_tag:
        return h_tag.get_text(strip=True)
    else:
        return ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")
    if main:
        main_p = main.find("p")
        if main_p:
            return main_p.get_text(strip=True)
        else:
            return ""
    paragraph = soup.find("p")
    if paragraph:
        return paragraph.get_text(strip=True)
    else:
        return ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    link_tags = soup.find_all("a")
    result = []
    for tag in link_tags:
        value = tag.get("href")
        if value:
            final_url = urljoin(base_url, value)
            result.append(final_url)
    return result

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")
    result = []
    for tag in img_tags:
        value = tag.get("src")
        if value:
            final_url = urljoin(base_url, value)
            result.append(final_url)
    return result

def extract_page_data(html: str, page_url: str) -> PageData:
    result = {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }
    return result 

async def crawl_site_async(base_url: str):
    async with AsyncCrawler(base_url) as crawler:
        return await crawler.crawl()

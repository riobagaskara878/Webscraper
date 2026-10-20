from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict


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

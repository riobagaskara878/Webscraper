import sys
import requests
from urllib.parse import urlparse
from crawl import (
    normalize_url,
    extract_page_data,
)

def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")
    crawled_page_data = crawl_page(sys.argv[1])
    print(f"Total pages found: {len(crawled_page_data)}")
    for page in crawled_page_data.values():
        print(page)

def get_html(url):
    response = requests.get(
    url,
    headers={"User-Agent": "SomeCrawlerName/1.0"},
)
    response.raise_for_status()
    content_type = response.headers.get("content-type")
    if content_type is None or not content_type.startswith("text/html"):
        raise Exception("response is not HTML")
    return response.text

def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}
    if urlparse(current_url).netloc != urlparse(base_url).netloc:
        return page_data
    normalize_current = normalize_url(current_url)
    if normalize_current in page_data:
        return page_data
    html = get_html(current_url)
    print(f"fetching: {current_url}")
    if html is None:
        return page_data
    page_data[normalize_current] = extract_page_data(html, current_url)
    outgoing_links = page_data[normalize_current]["outgoing_links"]
    for link in outgoing_links:
        crawl_page(base_url, link, page_data)
    return page_data




if __name__ == "__main__":
    main()

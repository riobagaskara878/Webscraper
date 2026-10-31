import sys
import requests
import asyncio
from urllib.parse import urlparse
from crawl import (
    normalize_url,
    extract_page_data,
    crawl_site_async,
)

async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    elif len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    else:
        print(f"starting crawl of: {sys.argv[1]}")
    crawled_page_data = await crawl_site_async(sys.argv[1])
    print(f"Total pages found: {len(crawled_page_data)}")
    for page in crawled_page_data.values():
        print(page)


if __name__ == "__main__":
    asyncio.run(main())

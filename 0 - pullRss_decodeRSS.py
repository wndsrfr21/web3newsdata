import json
import aiohttp
import asyncio
import xml.etree.ElementTree as ET
from urllib.parse import quote, urlparse
from bs4 import BeautifulSoup

# List of RSS feeds to parse
rss_feeds = [
    "https://news.google.com/rss/search?q=web3%20defi%20raised%202024&hl=en-US&gl=US&ceid=US%3Aen",
    # Add more feeds here in the future
]

async def fetch(session, url):
    """Fetch a URL asynchronously."""
    async with session.get(url) as response:
        return await response.text()

async def parse_feed(session, feed_url: str) -> list:
    """Parse a single RSS feed and return a list of entries."""
    entries = []
    try:
        async with session.get(feed_url) as response:
            response_text = await response.text()
            root = ET.fromstring(response_text)
            for item in root.findall('.//item'):
                link = item.find('link').text if item.find('link') is not None else ''
                entries.append(link)
    except Exception as e:
        print(f"Error parsing feed {feed_url}: {str(e)}")
    return entries

async def decode_urls(session, articles):
    """Decode the provided list of Google News URLs asynchronously."""
    articles_reqs = [
        [
            "Fbv4je",
            f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{art["gn_art_id"]}",{art["timestamp"]},"{art["signature"]}"]',
        ]
        for art in articles
    ]
    payload = f"f.req={quote(json.dumps([articles_reqs]))}"
    headers = {"content-type": "application/x-www-form-urlencoded;charset=UTF-8"}
    async with session.post(
        url="https://news.google.com/_/DotsSplashUi/data/batchexecute",
        headers=headers,
        data=payload,
    ) as response:
        response_text = await response.text()
        return [json.loads(res[2])[1] for res in json.loads(response_text.split("\n\n")[1])[:-2]]

async def process_url(session, url: str) -> str:
    """Process a single URL asynchronously and decode if necessary."""
    try:
        gn_art_id = urlparse(url).path.split("/")[-1]
        
        # Fetch the article page to scrape necessary parameters
        article_url = f"https://news.google.com/articles/{gn_art_id}"
        article_text = await fetch(session, article_url)
        
        # Scrape the page for decoding parameters
        soup = BeautifulSoup(article_text, "lxml")
        div = soup.select_one("c-wiz > div")
        params = {
            "signature": div.get("data-n-a-sg"),
            "timestamp": div.get("data-n-a-ts"),
            "gn_art_id": gn_art_id,
        }
        
        # Decode the URL
        decoded_url = await decode_urls(session, [params])
        return decoded_url[0]  # Return the first (and only) decoded URL
    except Exception as e:
        print(f"Decoding failed for URL: {url}. Error: {str(e)}")
        return url  # Return the original URL if decoding fails

async def process_urls(session, rss_urls: set) -> set:
    """Process all URLs asynchronously."""
    tasks = [process_url(session, url) for url in rss_urls]
    decoded_urls = await asyncio.gather(*tasks)
    return set(decoded_urls)

async def main():
    """Main function to parse feeds, decode URLs, and print the result."""
    async with aiohttp.ClientSession() as session:
        # Parse all feeds concurrently
        rss_urls = set()
        feed_tasks = [parse_feed(session, feed_url) for feed_url in rss_feeds]
        feed_results = await asyncio.gather(*feed_tasks)

        # Flatten the list of lists into a set of URLs
        for result in feed_results:
            rss_urls.update(result)

        # Process and decode URLs concurrently
        decoded_urls = await process_urls(session, rss_urls)

        # Print the result
        print(json.dumps(list(decoded_urls), indent=2))

# For local testing
if __name__ == "__main__":
    asyncio.run(main())

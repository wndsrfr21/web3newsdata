import json
import urllib.request
import xml.etree.ElementTree as ET
from http.client import HTTPResponse
from typing import Dict, Any

# List of RSS feeds to parse
rss_feeds = [
    "https://news.google.com/rss/search?q=web3%20defi%20raised%202024&hl=en-US&gl=US&ceid=US%3Aen",
    # Add more feeds here in the future
    # "https://example.com/feed1",
    # "https://example.com/feed2",
]

def parse_feed(feed_url: str) -> list:
    """Parse a single RSS feed and return a list of entries."""
    entries = []
    try:
        with urllib.request.urlopen(feed_url) as response:
            tree = ET.parse(response)
            root = tree.getroot()
            for item in root.findall('.//item'):
                title = item.find('title').text if item.find('title') is not None else ''
                link = item.find('link').text if item.find('link') is not None else ''
                entries.append({
                    "url": link,
                    "title": title
                })
    except Exception as e:
        print(f"Error parsing feed {feed_url}: {str(e)}")
    return entries

def parse_all_feeds() -> list:
    """Parse all RSS feeds and return a combined list of entries."""
    all_entries = []
    for feed_url in rss_feeds:
        all_entries.extend(parse_feed(feed_url))
    return all_entries

def main(args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to be executed by DigitalOcean Functions.
    
    :param args: Dictionary of arguments passed to the function
    :return: Dictionary containing the function's response
    """
    try:
        # Parse all feeds
        entries = parse_all_feeds()

        # Convert the list to a set to remove any duplicates
        unique_entries = {json.dumps(entry) for entry in entries}

        # Convert the set back to a list of dictionaries
        output = [json.loads(entry) for entry in unique_entries]

        # Return the result
        return {
            "statusCode": 200,
            "body": json.dumps(output)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }

# This is required for DigitalOcean Functions
def main_wrapper(args: Dict[str, Any], kwargs: Dict[str, Any]) -> HTTPResponse:
    return main(args)

# For local testing
if __name__ == "__main__":
    result = main({})
    print(json.dumps(result, indent=2))

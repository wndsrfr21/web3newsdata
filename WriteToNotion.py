# This code writes data to Notion and is functional

def add_to_notion(title, url):
    print(f"Attempting to add to Notion - Title: {title}, URL: {url}")
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }

    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Title": {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": title
                        }
                    }
                ]
            },
            "URL": {
                "url": url
            }
        }
    }

    try:
        response = requests.post(NOTION_API_URL, headers=headers, json=data)
        response.raise_for_status()
        print(f"Notion API response status code: {response.status_code}")
        print("Response:", response.json())
        return True
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
        if response.text:
            print("Response content:", response.text)
        return False

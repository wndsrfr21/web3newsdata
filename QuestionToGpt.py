import openai
import requests
from bs4 import BeautifulSoup

# Define your OpenAI API key securely
openai.api_key = 'your-new-api-key-here'

def fetch_article_content(url):
    """Fetches and returns the text content of an article from a given URL."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            paragraphs = soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
            return article_text
        else:
            return f"Error: Unable to fetch article content, status code {response.status_code}"
    except Exception as e:
        return f"Error: {e}"

def ask_chatgpt_for_json(article_text):
    """Sends the article text to GPT and retrieves the extracted information in JSON format."""
    messages = [
        {"role": "system", "content": "You are an AI assistant that extracts structured data from articles."},
        {"role": "user", "content": f"""
        For the following article, can you tell me the following in JSON compatible with Notion with this format:
        <english word> (notion db variable name)

        startup name (Company) / startup website url (StartupWebsite) / funding amount (FundingAmount) / funding date (FundingDate) / Date the article was published (ArticlePublishDate) / investors (Investors).

        For the startup website URL, please search for the startup company name that you find in the article and find their corporate website.

        Here is the article:
        {article_text}
        """}
    ]

    try:
        # Use the new API method
        response = openai.chat_completions.create(
            model="gpt-3.5-turbo",  # or use 'gpt-4' if you have access
            messages=messages,
            max_tokens=500  # Adjust based on the length of the article and response expected
        )
        
        # Correct way to access the response content in the new API version
        answer = response['choices'][0]['message']['content'].strip()
        return answer
    except Exception as e:
        return f"Error: {e}"

def main(url):
    """Main function to fetch the article, send it to GPT, and print the extracted JSON."""
    # Step 1: Fetch article content from the provided URL
    article_text = fetch_article_content(url)

    # Check if article fetching was successful
    if "Error" in article_text:
        print(article_text)
        return

    # Step 2: Ask GPT to extract the required information in JSON format
    json_result = ask_chatgpt_for_json(article_text)

    # Step 3: Print the result (or you can store it in Notion or elsewhere)
    print("Extracted JSON from GPT:")
    print(json_result)

# Example usage:
if __name__ == "__main__":
    # Use the provided URL to analyze
    url = "https://cryptodaily.co.uk/2024/08/lending-protocol-echelon-closes-35m-seed-round-with-cypher-capital"
    main(url)

# This code writes data to a github file

import json
import requests
import os
from base64 import b64encode, b64decode

# GitHub credentials
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
REPO_OWNER = 'wndsrfr21'
REPO_NAME = 'web3newsdata'
FILE_PATH = 'web3news.json'
BRANCH = 'main'

# Test URL
TEST_URL = "https://www.google.com"

def get_github_headers():
    token = os.getenv('GITHUB_TOKEN')
    if not token:
        raise Exception("GitHub token not found. Make sure it's set correctly as an environment variable.")
    return {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

def get_file_content(repo_owner, repo_name, file_path, branch):
    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}'
    headers = get_github_headers()
    response = requests.get(url, headers=headers)
    
    print(f"Request URL: {url}")
    print(f"Response status code: {response.status_code}")
    
    if response.status_code == 200:
        file_info = response.json()
        content = file_info.get('content', '')
        sha = file_info.get('sha')
        
        if content:
            decoded_content = b64decode(content).decode('utf-8').strip()
            print(f"Decoded content: {decoded_content}")
            
            if decoded_content:
                try:
                    return json.loads(decoded_content), sha
                except json.JSONDecodeError:
                    print("File exists but contains invalid JSON. Starting with an empty dictionary.")
                    return {}, sha
            else:
                print("File exists but is empty. Starting with an empty dictionary.")
                return {}, sha
        else:
            print("File exists but has no content. Starting with an empty dictionary.")
            return {}, sha
    elif response.status_code == 404:
        print("File not found. A new file will be created.")
        return None, None
    else:
        print(f"Unexpected error. Response content: {response.text}")
        raise Exception(f"Error retrieving file content: {response.status_code}")

def write_json_to_github(repo_owner, repo_name, file_path, json_data, branch='main', sha=None):
    json_str = json.dumps(json_data, indent=4)
    json_bytes = json_str.encode('utf-8')
    encoded_content = b64encode(json_bytes).decode('utf-8')
    
    commit_message = 'Update JSON file programmatically'
    data = {
        'message': commit_message,
        'content': encoded_content,
        'branch': branch,
    }
    
    if sha:
        data['sha'] = sha

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}'
    headers = get_github_headers()
    response = requests.put(url, headers=headers, json=data)
    
    print(f"Request URL: {url}")
    print(f"Response status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code in [200, 201]:
        return {"message": "File successfully committed to GitHub."}
    else:
        return {"error": f"Failed to commit file: {response.status_code}, {response.text}"}

def add_url_to_json(url):
    try:
        content, sha = get_file_content(REPO_OWNER, REPO_NAME, FILE_PATH, BRANCH)
        
        if content is None:
            json_data = {"unique_links": [url]}
        else:
            if "unique_links" not in content:
                content["unique_links"] = []
            if url not in content["unique_links"]:
                content["unique_links"].append(url)
            json_data = content

        response = write_json_to_github(REPO_OWNER, REPO_NAME, FILE_PATH, json_data, BRANCH, sha)
        return response
    except Exception as e:
        return {"error": str(e)}

def main():
    print(f"GitHub Token (first 10 characters): {GITHUB_TOKEN[:10] if GITHUB_TOKEN else 'Not set'}")
    response = add_url_to_json(TEST_URL)
    print("Final response:", response)
    return response

if __name__ == "__main__":
    main()

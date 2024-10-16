import requests
import base64
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Define variables from the .env file
repo_owner = os.getenv("REPO_OWNER")
repo_name = os.getenv("REPO_NAME")
file_path = os.getenv("FILE_PATH")
commit_message = os.getenv("COMMIT_MESSAGE")
github_token = os.getenv("GITHUB_TOKEN")

def get_file_sha(repo_owner, repo_name, file_path, token):
    """ Get the SHA of the existing file (if it exists) to update it. """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json().get("sha")
    return None

def write_set_to_github(repo_owner, repo_name, file_path, set_data, commit_message, token):
    """ Write a Python set to a file in a GitHub repository. """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}
    
    # Convert the set to a string to write to the file
    content = "\n".join(set_data)
    
    # GitHub requires the file content to be base64 encoded
    encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    
    # Check if the file already exists to get its SHA (required for updates)
    file_sha = get_file_sha(repo_owner, repo_name, file_path, token)
    
    # Create the payload for the request
    data = {
        "message": commit_message,
        "content": encoded_content,
        "branch": "main"  # or your target branch
    }
    
    if file_sha:
        data["sha"] = file_sha  # Required for updates
    
    response = requests.put(url, headers=headers, data=json.dumps(data))
    
    if response.status_code == 201 or response.status_code == 200:
        print("File successfully updated on GitHub!")
    else:
        print(f"Failed to update file: {response.status_code}, {response.json()}")

def read_file_from_github(repo_owner, repo_name, file_path, token):
    """Read a file from a GitHub repository and return its content as a set of URLs."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        file_content = response.json().get("content", "")
        decoded_content = base64.b64decode(file_content).decode("utf-8")
        print(f"File Content:\n{decoded_content}")

        # Split the content by newlines and convert to a set
        urls_set = set(decoded_content.strip().splitlines())
        print(f"Parsed URLs Set:\n{urls_set}")
        return urls_set
    else:
        print(f"Failed to read file: {response.status_code}, {response.json()}")
        return set()

def clear_github_file(repo_owner, repo_name, file_path, github_token, commit_message="Clearing file"):
    
    # Step 1: Write an empty JSON structure to the file (empty list or empty set)
    empty_content = []  # This can be [] or {} depending on the structure you use in the JSON file
    write_set_to_github(repo_owner, repo_name, file_path, empty_content, commit_message, github_token)
    
    print("File has been cleared.")

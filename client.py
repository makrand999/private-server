
import requests
import threading
import time
import os
import json
import sys


GIST_ID = "7a5f94bf1d957c88537df19018b031e8"
GITHUB_TOKEN = "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"


SERVER_URL = "http://localhost:8000"
username = ""
last_message_id = -1

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_messages(messages):
    for message in messages:
       
        print(f"\r {message['username']}: {message['text']}                                 ")

def get_server_url_from_gist():
    """Fetch the server URL from GitHub Gist"""
    global SERVER_URL
    
    print("Fetching server URL from GitHub Gist...")
    
    try:
        gist_url = f"https://api.github.com/gists/{GIST_ID}"
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        response = requests.get(gist_url, headers=headers)
        response.raise_for_status()
        
        gist_data = response.json()
        if "cloudflare_tunnel_url.txt" in gist_data["files"]:
            url_content = gist_data["files"]["cloudflare_tunnel_url.txt"]["content"]
            if url_content.strip():
                SERVER_URL = url_content.strip()
                print(f"Connected to server at: {SERVER_URL}")
                return True
            
        print("No valid URL found in Gist. Using default: http://localhost:8000")
        return False
        
    except Exception as e:
        print(f"Error fetching server URL from Gist: {e}")
        print("Using default URL: http://localhost:8000")
        return False

def get_messages():
    global last_message_id
    
    while True:
        try:
            response = requests.get(f"{SERVER_URL}/messages?last_id={last_message_id}")
            if response.status_code == 200:
                new_messages = response.json()
                if new_messages:
                    display_messages(new_messages)
                    last_message_id = new_messages[-1]['id']
            time.sleep(1)
        except Exception as e:
            print(f"Error fetching messages: {e}")
            time.sleep(5)

def main():
    global username
    
    
    get_server_url_from_gist()
    

    try:
        response = requests.get(f"{SERVER_URL}")
        if response.status_code != 200:
            print(f"Warning: Server returned status code {response.status_code}")
    except Exception as e:
        print(f"Warning: Could not connect to server: {e}")
        retry = input("Continue anyway? (y/n): ")
        if retry.lower() != 'y':
            sys.exit(0)
    
 
    username = input("Enter your username: ")
    clear_screen()
    print(f"Welcome to the chat, {username}!")
    print(f"Connected to: {SERVER_URL}")
    print("Type your messages below. Press Ctrl+C to exit.")
    print("-" * 50)
    
  
    polling_thread = threading.Thread(target=get_messages, daemon=True)
    polling_thread.start()
    
    
    try:
        requests.post(f"{SERVER_URL}/send", 
                    json={"username": username, "text": "has joined the chat"})
    except Exception as e:
        print(f"Error sending join message: {e}")
    
    try:
        while True:
            message = input()
            sys.stdout.write("\033[F                                                \r")
            if message.strip():
                requests.post(f"{SERVER_URL}/send", 
                            json={"username": username, "text": message})
    except KeyboardInterrupt:
       
        try:
            requests.post(f"{SERVER_URL}/send", 
                        json={"username": username, "text": "has left the chat"})
        except:
            pass
        print("\nGoodbye!")

if __name__ == "__main__":
    main()

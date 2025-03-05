import os
import requests
import csv
import sys

TOKEN_FILE = "./tillay8_token"

def get_token():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.readline().strip()

header_data = {
    "Content-Type": "application/json",
    "Authorization": get_token()
}

def get_most_recent_messages(channel_id, before_id, limit):
    url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    params = {"limit": limit}
    if before_id:
        params["before"] = before_id
    response = requests.get(url, headers=header_data, params=params)
    if response.status_code == 200:
        messages = response.json()
        new_before_id = messages[-1]["id"] if messages else None
        return messages, new_before_id
    else:
        print(f"Failed to fetch messages. Status code: {response.status_code}")
        return None, None

def save_messages_to_csv(channel_id, limit, filename):
    total_messages_to_fetch = int(limit)
    messages_fetched = 0
    before_id = None

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Message"])

    while messages_fetched < total_messages_to_fetch:
        remaining_messages = total_messages_to_fetch - messages_fetched
        current_batch_size = min(100, remaining_messages)
        messages, before_id = get_most_recent_messages(channel_id, before_id, current_batch_size)

        if isinstance(messages, list):
            with open(filename, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                for message in messages:
                    writer.writerow([message['content']])
            messages_fetched += len(messages)
            print(f"Saved {messages_fetched} message(s) to {filename}. {remaining_messages} more to go")
        else:
            print("Error fetching messages.")
            break

filename = "messages.csv"
if len(sys.argv) < 3:
    print("Usage: python3 downloader.py <channel_id> <num_messages> <file_name>")
    sys.exit(1)

elif len(sys.argv) == 3:
    channel_id = sys.argv[1]
    num_messages = sys.argv[2]
if len(sys.argv) > 3:
    filename = sys.argv[3]

save_messages_to_csv(channel_id, num_messages, filename)

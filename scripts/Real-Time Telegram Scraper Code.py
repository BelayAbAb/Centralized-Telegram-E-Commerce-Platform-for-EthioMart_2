import telethon
import pandas as pd
import re
import os
from telethon import TelegramClient, events

# Use your actual API ID and API Hash
api_id = '26737733'
api_hash = 'f590cc7e473a4e1c9ea4f7bc59163016'
client = TelegramClient('session_name', api_id, api_hash)

# List of Telegram channels to scrape
channels = [
    '@Leyueqa', '@sinayelj'
]


# Preprocessed data storage
preprocessed_data = []

def preprocess_text(text):
    # Tokenization: split into tokens
    tokens = re.findall(r'\w+', text)  # Basic tokenization
    # Normalization: removing special characters
    normalized_tokens = [token.lower() for token in tokens]
    return normalized_tokens

def save_preprocessed_data(data, filename):
    df = pd.DataFrame(data, columns=['metadata', 'content'])
    df.to_csv(filename, index=False, mode='a', header=not os.path.exists(filename))

@client.on(events.NewMessage(channels))
async def handler(event):
    # Preprocess the new message
    preprocessed_content = preprocess_text(event.message.message)
    metadata = {
        'sender': event.message.sender_id,
        'timestamp': event.message.date
    }
    preprocessed_data.append((metadata, preprocessed_content))
    
    # Save to CSV every 10 messages to avoid too frequent I/O operations
    if len(preprocessed_data) >= 10:
        save_preprocessed_data(preprocessed_data, 'preprocessed_data.csv')
        preprocessed_data.clear()  # Clear the list after saving

async def main():
    await client.start()
    print("Listening for new messages...")

    # Keep the script running
    await client.run_until_disconnected()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

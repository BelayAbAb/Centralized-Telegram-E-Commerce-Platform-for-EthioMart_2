import telethon
import pandas as pd
import re
from telethon import TelegramClient

# Use your actual API ID and API Hash
api_id = '26737733'
api_hash = 'f590cc7e473a4e1c9ea4f7bc59163016'
client = TelegramClient('session_name', api_id, api_hash)

# List of Telegram channels to scrape
channels = [
    '@Leyueqa', '@sinayelj'
]

async def fetch_messages(channel):
    await client.start()
    messages = await client.get_messages(channel, limit=100)
    return messages

def preprocess_text(text):
    # Normalize: removing special characters and converting to lowercase
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)  # Remove special characters
    text = text.lower()  # Convert to lowercase

    # Tokenization: split into tokens
    tokens = re.findall(r'\w+', text)  # Basic tokenization
    token_count = len(tokens)
    
    return tokens, token_count

def save_preprocessed_data(data, filename):
    records = []
    for metadata, tokens in data:
        record = {'sender': metadata['sender'], 'timestamp': metadata['timestamp']}
        for i, token in enumerate(tokens):
            record[f'token_{i + 1}'] = token
        records.append(record)

    df = pd.DataFrame(records)
    df.to_csv(filename, index=False)

async def main():
    all_data = []

    for channel in channels:
        messages = await fetch_messages(channel)
        for message in messages:
            preprocessed_content, token_count = preprocess_text(message.text)
            metadata = {
                'sender': message.sender_id,
                'timestamp': message.date,
                'token_count': token_count
            }
            all_data.append((metadata, preprocessed_content))

    save_preprocessed_data(all_data, 'preprocessed_data.csv')

def label_data_for_conll(messages):
    labeled_data = []
    for msg in messages:
        tokens = msg[1]
        for token in tokens:
            # Entity labeling logic
            entity_label = 'O'  # Default label for no entity

            # Simple entity identification
            if re.match(r'^[\d]+$', token):  # If the token is a number, label as Price
                entity_label = 'B-Price'
            elif re.match(r'^[A-Za-z\s]+$', token):  # If the token is alphabetic, check for products
                entity_label = 'B-Product' if 'product' in token.lower() else entity_label
            elif re.match(r'\b\w+\b', token):  # Simple heuristic for locations
                entity_label = 'B-Location' if token.lower() in ['addis ababa', 'dire dawa'] else entity_label
            
            labeled_data.append(f"{token} {entity_label}")

        labeled_data.append("")  # Separate messages with a blank line

    # Save to a CoNLL format file
    with open('labeled_preprocessed_data.conll', 'w') as f:
        f.write('\n'.join(labeled_data))

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

    # Load the preprocessed data to label a subset
    preprocessed_df = pd.read_csv('preprocessed_data.csv')
    subset_messages = preprocessed_df.sample(n=50).to_records(index=False)  # Randomly select 50 messages for labeling
    label_data_for_conll(subset_messages)

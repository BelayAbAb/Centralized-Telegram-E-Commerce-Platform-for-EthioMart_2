import telethon
import pandas as pd
import re
import matplotlib.pyplot as plt
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
            entity_label = 'O'  # Default label for no entity

            # Simple entity identification
            if re.match(r'^[\d]+$', token):  # If the token is a number, label as Price
                entity_label = 'B-Price'
            elif re.match(r'^[A-Za-z\s]+$', token):  # If the token is alphabetic
                entity_label = 'B-Product' if 'product' in token.lower() else entity_label
            elif re.match(r'\b\w+\b', token):  # Simple heuristic for locations
                entity_label = 'B-Location' if token.lower() in ['addis ababa', 'dire dawa'] else entity_label
            
            labeled_data.append(f"{token} {entity_label}")

        labeled_data.append("")  # Separate messages with a blank line

    with open('labeled_preprocessed_data.conll', 'w') as f:
        f.write('\n'.join(labeled_data))

def summarize_labeled_data(filename):
    entity_counts = {'B-Product': 0, 'B-Price': 0, 'B-Location': 0, 'O': 0}
    total_tokens = 0
    total_messages = 0
    tokens_per_message = []

    with open(filename, 'r') as f:
        current_message_tokens = 0
        for line in f:
            if line.strip():  # If the line is not blank
                token, label = line.rsplit(' ', 1)
                total_tokens += 1
                current_message_tokens += 1
                if label in entity_counts:
                    entity_counts[label] += 1
            else:
                if current_message_tokens > 0:
                    tokens_per_message.append(current_message_tokens)
                    total_messages += 1
                current_message_tokens = 0  # Reset for the next message

    # Handle last message if the file does not end with a newline
    if current_message_tokens > 0:
        tokens_per_message.append(current_message_tokens)
        total_messages += 1

    average_tokens = total_tokens / total_messages if total_messages > 0 else 0

    # Create a statistics report
    plt.figure(figsize=(12, 8))

    # Entity counts bar chart
    plt.subplot(311)
    plt.bar(entity_counts.keys(), entity_counts.values(), color=['blue', 'green', 'orange', 'gray'])
    plt.title('Entity Count Summary')
    plt.xlabel('Entity Types')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    # Total messages and tokens
    plt.subplot(312)
    plt.bar(['Total Messages', 'Total Tokens'], [total_messages, total_tokens], color=['purple', 'red'])
    plt.title('Total Messages and Tokens')
    plt.ylabel('Count')
    plt.xticks(rotation=45)
    plt.grid(axis='y')

    # Distribution of tokens per message
    plt.subplot(313)
    plt.hist(tokens_per_message, bins=range(1, max(tokens_per_message) + 2), color='skyblue', edgecolor='black')
    plt.title('Distribution of Tokens per Message')
    plt.xlabel('Number of Tokens')
    plt.ylabel('Number of Messages')
    plt.grid(axis='y')

    # Save the figure as a JPG file
    plt.tight_layout()
    plt.savefig('statistics_report.jpg')
    plt.close()

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())

    preprocessed_df = pd.read_csv('preprocessed_data.csv')
    subset_messages = preprocessed_df.sample(n=50).to_records(index=False)  # Randomly select 50 messages for labeling
    label_data_for_conll(subset_messages)

    summarize_labeled_data('labeled_preprocessed_data.conll')

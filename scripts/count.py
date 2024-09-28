def preprocess_text(text):
    # Tokenization: split into tokens
    tokens = re.findall(r'\w+', text)  # Basic tokenization
    # Normalization: removing special characters
    normalized_tokens = [token.lower() for token in tokens]
    
    # Count tokens
    token_count = len(normalized_tokens)
    
    return normalized_tokens, token_count

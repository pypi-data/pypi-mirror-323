def humanize_input(message: str) -> str:
    """
    Transforms a given string into a standardized, machine-friendly format by converting it 
    to lowercase and replacing spaces with underscores. It also handles plural forms, 
    such as converting 'meters' to 'meter' and special cases like 'feet' to 'foot'.
    Additional special handling for 'm/s', 'siemens', and 'celsius'.

    Parameters:
    message (str): The input string to be transformed.

    Returns:
    str: The transformed string, with:
         - All characters in lowercase.
         - Plural forms converted to singular (e.g., 'meters' -> 'meter').
         - Spaces replaced by underscores.
         - Special cases like 'feet' handled explicitly (e.g., 'feet' -> 'foot').
    """
    # Handle special cases
    if message.lower() == 'feet':
        message = 'foot'
    elif message.lower() == 'siemens':
        return 'siemens'  # No change for 'siemens'
    elif message.lower() == 'celsius':
        return 'celsius'  # No change for 'celsius'
    elif message.lower() == 'm/s':
        return 'meter_per_second'  # Handle 'm/s' directly
    
    # Normalize the message
    normalized = message.lower().strip()

    # Split the message into words and handle plural forms
    words = normalized.split()
    normalized_words = [
        word[:-1] if word.endswith('s') and not word.endswith('ss') else word
        for word in words
    ]

    # Join the words with underscores
    normalized = '_'.join(normalized_words)
    return normalized

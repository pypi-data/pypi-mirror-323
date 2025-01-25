# __init__.py

from .stopwords import STOPWORDS

def remove_stopwords(text):
    """
    Remove Somali stopwords from the input text.
    
    Parameters:
    text (str): The input text from which stopwords will be removed.
    
    Returns:
    str: The text with stopwords removed.
    """
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in STOPWORDS]
    return ' '.join(filtered_words)

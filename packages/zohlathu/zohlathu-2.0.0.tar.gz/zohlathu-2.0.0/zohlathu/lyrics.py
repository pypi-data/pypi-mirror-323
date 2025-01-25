import feedparser
import html2text
import re
from typing import Dict

def get_lyrics(query: str) -> Dict[str, str]:
    """
    Fetch lyrics for the given song query
    
    Args:
        query (str): Song name or artist to search for
        
    Returns:
        dict: Dictionary containing title and lyrics
    """
    base_url = "https://www.blogger.com/feeds/690973182178026088/posts/default"
    search_query = query.replace(' ', '+')
    feed_url = f'{base_url}?q={search_query}'
    
    feed = feedparser.parse(feed_url)
        
    for entry in feed.entries:
        content = html2text.html2text(entry.content[0]['value'])
        pattern = r'\* \* \*(.*?)\* \* \*'
        cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)
            
        return {
            "title": entry.title,
            "lyrics": cleaned_content.strip(),
            "source_url": entry.link,
        }
    return None

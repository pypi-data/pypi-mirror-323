import feedparser
import html2text
import re
import time
from typing import Dict, Optional
from youtube_search import YoutubeSearch

def get_lyrics(query: str, max_retries: int = 3) -> Optional[Dict[str, str]]:
    """
    Fetch lyrics for the given song query
   
    Args:
        query (str): Song name or artist to search for
        max_retries (int): Maximum number of retry attempts
       
    Returns:
        dict: Dictionary containing title and lyrics, or None if not found
    """
    # Configure headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'application/atom+xml,text/html'
    }

    try:
        time.sleep(3)
        # Validate input
        if not query or not isinstance(query, str):
            raise ValueError("Invalid search query. Must be a non-empty string.")
        
        base_url = "https://www.blogger.com/feeds/690973182178026088/posts/default"
        
        try:
            # Perform YouTube search
            results = YoutubeSearch(f"{query}", max_results=1).to_dict()
            
            if not results:
                print(f"No YouTube results found for query: {query}")
                return None
            
            titlep = results[0]["title"][:100]
            search_query = titlep.replace(' ', '+')
            feed_url = f'{base_url}?q={search_query}'
        
        except Exception as youtube_error:
            print(f"YouTube search error: {youtube_error}")
            return None
        
        # Parse feed with headers
        try:
            # Add headers to feedparser
            feed = feedparser.parse(feed_url, request_headers=headers)
            
            if not feed.entries:
                print(f"No entries found in feed for query: {query}")
                return None
            
            # Process first entry
            entry = feed.entries[0]
            
            # Extract and clean content
            content = html2text.html2text(entry.content[0]['value'])
            pattern = r'\* \* \*(.*?)\* \* \*'
            cleaned_content = re.sub(pattern, '', content, flags=re.DOTALL)
               
            return {
                "title": entry.title,
                "lyrics": cleaned_content.strip(),
                "source_url": entry.link,
            }
        
        except IndexError:
            print(f"No content found in feed entries for query: {query}")
            return None
        
        except Exception as feed_error:
            print(f"Feed parsing error: {feed_error}")
            return None
    
    except ValueError as val_error:
        print(f"Input validation error: {val_error}")
        return None
    
    except Exception as general_error:
        print(f"Unexpected error occurred: {general_error}")
        return None

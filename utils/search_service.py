"""
Search Service Module
Handles search suggestions from Google
"""

import requests
import json
import logging
from typing import List

logger = logging.getLogger(__name__)

def get_search_suggestions(query: str, **kwargs) -> List[str]:
    """
    Get search suggestions from Google
    
    Args:
        query: Search query string
        **kwargs: Additional parameters (unused but needed for compatibility)
        
    Returns:
        List of search suggestions
    """
    try:
        # Google's autocomplete API
        url = f"http://google.com/complete/search?client=chrome&q={query}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582"
        }
        
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        results = json.loads(response.text)[1]
        
        # Insert the user input as the first option
        if query not in results:
            results.insert(0, query)
        
        return results[:10]  # Limit to 10 suggestions
        
    except requests.RequestException as e:
        logger.error(f"Error fetching search suggestions: {e}")
        return [query]  # Return just the query if fetch fails
    except (json.JSONDecodeError, IndexError) as e:
        logger.error(f"Error parsing search suggestions: {e}")
        return [query]
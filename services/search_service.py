import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SearchService:
    """Service for handling web search operations"""
    
    def __init__(self):
        """Initialize the search service with API keys"""
        self.google_api_key = os.getenv('GOOGLE_SEARCH_API_KEY')
        self.google_cx = os.getenv('GOOGLE_SEARCH_CX')  # Custom Search Engine ID
        self.bing_api_key = os.getenv('BING_SEARCH_API_KEY')
        self.search_engine = os.getenv('SEARCH_ENGINE', 'google')  # Default to Google
    
    def search_web(self, query, num_results=5):
        """Search the web for information related to the query"""
        if self.search_engine.lower() == 'google':
            return self._google_search(query, num_results)
        elif self.search_engine.lower() == 'bing':
            return self._bing_search(query, num_results)
        else:
            raise ValueError(f"Unsupported search engine: {self.search_engine}")
    
    def _google_search(self, query, num_results=5):
        """Perform a Google search using the Custom Search JSON API"""
        if not self.google_api_key or not self.google_cx:
            raise ValueError("Google Search API key or Custom Search Engine ID not configured")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.google_api_key,
            'cx': self.google_cx,
            'q': query,
            'num': min(num_results, 10)  # Google API allows max 10 results per request
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            search_results = response.json()
            
            # Extract relevant information from search results
            results = []
            if 'items' in search_results:
                for item in search_results['items']:
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Google'
                    }
                    results.append(result)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error during Google search: {str(e)}")
            return []
    
    def _bing_search(self, query, num_results=5):
        """Perform a Bing search using the Bing Web Search API"""
        if not self.bing_api_key:
            raise ValueError("Bing Search API key not configured")
        
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            'Ocp-Apim-Subscription-Key': self.bing_api_key
        }
        params = {
            'q': query,
            'count': num_results,
            'responseFilter': 'Webpages'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()  # Raise an exception for HTTP errors
            
            search_results = response.json()
            
            # Extract relevant information from search results
            results = []
            if 'webPages' in search_results and 'value' in search_results['webPages']:
                for item in search_results['webPages']['value']:
                    result = {
                        'title': item.get('name', ''),
                        'link': item.get('url', ''),
                        'snippet': item.get('snippet', ''),
                        'source': 'Bing'
                    }
                    results.append(result)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error during Bing search: {str(e)}")
            return []
    
    def format_search_results(self, results, max_length=1000):
        """Format search results for inclusion in email replies"""
        if not results:
            return "No relevant information found."
        
        formatted = "Here's what I found on the web:\n\n"
        
        for i, result in enumerate(results, 1):
            result_text = f"{i}. {result['title']}\n"
            result_text += f"   {result['link']}\n"
            result_text += f"   {result['snippet']}\n\n"
            
            # Check if adding this result would exceed max length
            if len(formatted) + len(result_text) > max_length:
                formatted += "...\n(Additional results omitted for brevity)"
                break
                
            formatted += result_text
        
        return formatted
    
    def test_connection(self):
        """Test if the search service is properly configured"""
        try:
            # Perform a simple test search
            results = self.search_web("test query", 1)
            return len(results) > 0
        except Exception as e:
            print(f"Search service connection test failed: {str(e)}")
            return False

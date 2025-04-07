import requests
import json
from typing import List, Dict, Any, Optional
import os

from config import SEARCH_API_KEY, SEARCH_ENGINE_ID

class SearchIntegration:
    def __init__(self):
        self.api_key = SEARCH_API_KEY
        self.search_engine_id = SEARCH_ENGINE_ID
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Perform a web search using Google Custom Search API.
        
        Args:
            query: The search query
            num_results: Number of results to return (max 10)
            
        Returns:
            List of search results with title, link, and snippet
        """
        try:
            # Ensure we don't exceed the maximum allowed results
            num_results = min(num_results, 10)
            
            # Build the search URL
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': num_results
            }
            
            # Make the request
            response = requests.get(url, params=params)
            
            # Check if the request was successful
            if response.status_code != 200:
                print(f"Search API error: {response.status_code} - {response.text}")
                return []
            
            # Parse the results
            search_results = []
            data = response.json()
            
            if 'items' in data:
                for item in data['items']:
                    result = {
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    }
                    search_results.append(result)
            
            return search_results
        
        except Exception as e:
            print(f"Error performing search: {str(e)}")
            return []
    
    def format_results_for_llm(self, results: List[Dict[str, str]]) -> str:
        """
        Format search results in a way that's useful for the LLM.
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return "No search results found."
        
        formatted_text = "Search Results:\n\n"
        
        for i, result in enumerate(results, 1):
            formatted_text += f"{i}. {result['title']}\n"
            formatted_text += f"   URL: {result['link']}\n"
            formatted_text += f"   {result['snippet']}\n\n"
        
        return formatted_text
    
    def search_and_format(self, query: str, num_results: int = 5) -> str:
        """
        Perform a search and format the results in one step.
        
        Args:
            query: The search query
            num_results: Number of results to return
            
        Returns:
            Formatted string with search results
        """
        results = self.search(query, num_results)
        return self.format_results_for_llm(results)
    
    def enhance_email_with_search(self, email_content: str, search_query: Optional[str] = None) -> str:
        """
        Enhance an email response with relevant search results.
        
        Args:
            email_content: The content of the email
            search_query: Optional specific search query, if None will generate from email
            
        Returns:
            Search results formatted as text
        """
        # If no specific query is provided, use the email content
        if not search_query:
            # Use a simplified approach - in production you might use the LLM to generate a better query
            words = email_content.split()
            query = ' '.join(words[:10])  # Use first 10 words as a simple query
        else:
            query = search_query
        
        # Get search results
        results = self.search(query)
        
        # Format the results
        return self.format_results_for_llm(results)

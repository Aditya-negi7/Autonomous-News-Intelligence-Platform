import os
import logging
import requests
from typing import List, Dict, Any
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ResearcherAgent:
    """
    Agent responsible for fetching the latest world news using the Serper API.
    """
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/news"
        if not self.api_key:
            logger.error("SERPER_API_KEY is not set in the environment variables.")
            raise ValueError("SERPER_API_KEY is not set in the environment variables.")

    def fetch_latest_news(self, query: str = "latest world news", language: str = "en") -> List[Dict[str, str]]:
        """
        Fetches news articles related to the given query.
        
        Args:
            query (str): The search query to use. Defaults to 'latest world news'.
            
        Returns:
            List[Dict[str, str]]: A list of dictionaries containing title, link, snippet, and date for each article.
        """
        payload = {
            "q": query,
            "num": 20,
            "hl": language,
            "gl": "in"
        }
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            logger.info(f"Fetching news with query: '{query}'")
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            
            articles = self._parse_results(data)
            logger.info(f"Successfully fetched {len(articles)} articles.")
            return articles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching news from Serper API: {e}")
            return []

    def _parse_results(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parses the raw JSON response from Serper API into a structured format.
        """
        articles = []
        news_results = data.get("news", [])
        
        for item in news_results:
            article = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "date": item.get("date", "")
            }
            articles.append(article)
            
        return articles

# Example usage
if __name__ == "__main__":
    try:
        researcher = ResearcherAgent()
        news = researcher.fetch_latest_news()
        for i, n in enumerate(news[:3], 1):
            print(f"{i}. {n['title']} ({n['date']})\n   {n['link']}\n   {n['snippet']}\n")
    except Exception as e:
        print(f"Setup Error: {e}")

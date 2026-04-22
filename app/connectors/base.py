from abc import ABC, abstractmethod
from typing import List
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.schemas.article import RawArticle

class BaseConnector(ABC):
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url
        # Async HTTP client for high-speed scraping
        self.client = httpx.AsyncClient(timeout=15.0)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def fetch_data(self, url: str) -> str | dict:
        """Standardized fetch with exponential backoff for flaky APIs."""
        response = await self.client.get(url)
        response.raise_for_status()
        
        # If it's JSON, return a dict. If XML/RSS, return raw text.
        if "application/json" in response.headers.get("Content-Type", ""):
            return response.json()
        return response.text

    @abstractmethod
    async def fetch_and_normalize(self) -> List[RawArticle]:
        """Every child class must implement this to return our clean schema."""
        pass

    async def close(self):
        """Clean up the HTTP client."""
        await self.client.aclose()
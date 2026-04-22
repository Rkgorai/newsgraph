import feedparser
from datetime import datetime, timezone
from time import mktime
from typing import List

from app.connectors.base import BaseConnector
from app.schemas.article import RawArticle

class RSSConnector(BaseConnector):
    def __init__(self, source_name: str, feed_url: str):
        # We pass the RSS feed URL as the base_url
        super().__init__(source_name=source_name, base_url=feed_url)

    async def fetch_and_normalize(self) -> List[RawArticle]:
        raw_xml = await self.fetch_data(self.base_url)
        
        # Parse the XML string into a Python dictionary using feedparser
        feed = feedparser.parse(raw_xml)
        articles: List[RawArticle] = []

        for entry in feed.entries:
            # Safely extract published date, fallback to right now
            published_dt = datetime.now(timezone.utc)
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_dt = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)

            # Map the messy RSS data to our clean Pydantic model
            article = RawArticle(
                title=entry.title,
                content=entry.get('summary', ''), # RSS uses summary/description for content
                url=entry.link,
                source_name=self.source_name,
                published_at=published_dt,
                author=entry.get('author', None)
            )
            articles.append(article)

        return articles
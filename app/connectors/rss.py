import feedparser
import re
from datetime import datetime, timezone
from time import mktime
from typing import List

from app.connectors.base import BaseConnector
from app.schemas.article import RawArticle

class RSSConnector(BaseConnector):
    def __init__(self, source_name: str, feed_url: str):
        super().__init__(source_name=source_name, base_url=feed_url)

    async def fetch_and_normalize(self) -> List[RawArticle]:
        raw_xml = await self.fetch_data(self.base_url)
        feed = feedparser.parse(raw_xml)
        articles: List[RawArticle] = []

        for entry in feed.entries:
            # 1. Improved Content Extraction
            # RSS feeds are inconsistent; we check tags in order of 'richness'
            content = ""
            if hasattr(entry, 'content'):
                content = entry.content[0].value
            elif hasattr(entry, 'summary'):
                content = entry.summary
            elif hasattr(entry, 'description'):
                content = entry.description

            # 2. Clean HTML tags (keeps the database text-only for better LLM performance later)
            clean_content = re.sub(r'<[^>]+>', '', content).strip() if content else ""

            # 3. Handle Date
            published_dt = datetime.now(timezone.utc)
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_dt = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)

            # 4. Create the Model
            article = RawArticle(
                title=entry.title,
                content=clean_content, # Now using the cleaned/found content
                url=entry.link,
                source_name=self.source_name,
                published_at=published_dt,
                author=entry.get('author', "")
            )
            articles.append(article)

        return articles
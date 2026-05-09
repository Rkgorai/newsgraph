"""
News source management service - syncs sources from news_sources.json
"""
import json
import asyncio
from pathlib import Path
from typing import List, Dict

from app.core.database import AsyncSessionLocal
from app.models.source import NewsSource
from sqlalchemy import select, delete


def load_sources_from_json() -> List[Dict[str, str]]:
    """Load news sources from the JSON configuration file."""
    json_path = Path(__file__).parent.parent.parent / "news_sources.json"
    with open(json_path, "r") as f:
        return json.load(f)


async def sync_news_sources() -> Dict[str, int]:
    """
    Sync news sources from JSON file to database.
    - Insert new sources
    - Update existing sources (URL changes)
    - Delete sources that are no longer in JSON

    Returns:
        Dict with counts: {"added": n, "updated": n, "deleted": n}
    """
    json_sources = load_sources_from_json()
    json_urls = {s["url"] for s in json_sources}
    json_names = {s["url"]: s["name"] for s in json_sources}

    async with AsyncSessionLocal() as db:
        # Get all existing sources from DB
        result = await db.execute(select(NewsSource))
        existing_sources = result.scalars().all()
        existing_urls = {s.feed_url for s in existing_sources}
        existing_by_url = {s.feed_url: s for s in existing_sources}

        added = 0
        updated = 0
        deleted = 0

        # 1. Add new sources (in JSON but not in DB)
        for url in json_urls:
            if url not in existing_urls:
                source = NewsSource(
                    name=json_names[url],
                    feed_url=url,
                    is_active=True
                )
                db.add(source)
                added += 1

        # 2. Update existing sources (name changed)
        for url in json_urls:
            if url in existing_by_url:
                source = existing_by_url[url]
                if source.name != json_names[url]:
                    source.name = json_names[url]
                    updated += 1

        # 3. Delete sources (in DB but not in JSON)
        for url in existing_urls:
            if url not in json_urls:
                await db.execute(
                    delete(NewsSource).where(NewsSource.feed_url == url)
                )
                deleted += 1

        await db.commit()

    return {"added": added, "updated": updated, "deleted": deleted}


async def get_active_sources() -> List[NewsSource]:
    """Get all active news sources from the database."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(NewsSource).where(NewsSource.is_active == True)
        )
        return list(result.scalars().all())


async def get_sources_from_json() -> List[Dict[str, str]]:
    """Get sources directly from JSON file (for one-off scripts)."""
    return load_sources_from_json()


if __name__ == "__main__":
    # Test the sync
    result = asyncio.run(sync_news_sources())
    print(f"Sync result: {result}")
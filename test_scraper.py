"""
Test scraper - fetches news from RSS feeds and saves to database.
Uses news_sources.json for source configuration.
"""
import asyncio
import argparse
from app.connectors.rss import RSSConnector
from app.services.ingestion_service import save_articles_to_db
from app.services.source_service import sync_news_sources, get_active_sources, get_sources_from_json
from app.core.database import AsyncSessionLocal


async def fetch_and_save(source_name: str, feed_url: str):
    """Fetches a feed and saves it directly to PostgreSQL."""
    connector = RSSConnector(source_name=source_name, feed_url=feed_url)

    try:
        # 1. Fetch from the internet
        articles = await connector.fetch_and_normalize()

        # 2. Save to the database
        async with AsyncSessionLocal() as db:
            saved_count = await save_articles_to_db(db, source_name, feed_url, articles)

        print(f"✅ [{source_name}] Fetched {len(articles)} -> Saved {saved_count} NEW articles to DB!")
        return saved_count

    except Exception as e:
        print(f"❌ [{source_name}] Failed: {e}")
        return 0
    finally:
        await connector.close()


async def main(sync: bool = True, limit: int = None):
    print("Initializing Database Ingestion Scraper...\n")

    # 1. Optionally sync sources from JSON to DB
    if sync:
        print("🔄 Syncing sources from news_sources.json...")
        result = await sync_news_sources()
        print(f"✅ Source sync complete: {result}")

    # 2. Get active sources (from DB which is synced from JSON)
    sources = await get_active_sources()

    if not sources:
        print("⚠️ No active sources found. Run with --no-sync to use JSON directly.")
        # Fallback to reading directly from JSON
        sources = await get_sources_from_json()
        print(f"📋 Using {len(sources)} sources from JSON file")
    else:
        print(f"📋 Using {len(sources)} active sources from database")

    # 3. Optionally limit sources for testing
    if limit:
        sources = sources[:limit]
        print(f"🔧 Limited to {limit} sources for testing")

    # 4. Fire them all off at the exact same time
    if sources and isinstance(sources[0], dict):
        tasks = [fetch_and_save(s["name"], s["url"]) for s in sources]
    else:
        tasks = [fetch_and_save(s.name, s.feed_url) for s in sources]

    results = await asyncio.gather(*tasks)

    total_saved = sum(results)
    print(f"\n🐘 Database insertion complete! Total new articles: {total_saved}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test scraper for news ingestion")
    parser.add_argument(
        "--no-sync",
        action="store_true",
        help="Skip syncing sources from JSON to database"
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of sources to scrape (for testing)"
    )
    args = parser.parse_args()

    asyncio.run(main(sync=not args.no_sync, limit=args.limit))
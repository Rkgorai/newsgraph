import asyncio
from celery import shared_task
from app.connectors.rss import RSSConnector
from app.services.ingestion_service import save_articles_to_db
from app.services.source_service import get_active_sources, sync_news_sources
from app.core.database import AsyncSessionLocal


async def async_fetch_and_save(source_name: str, feed_url: str):
    """Bridge function to run async scraping inside sync Celery"""
    connector = RSSConnector(source_name=source_name, feed_url=feed_url)
    try:
        articles = await connector.fetch_and_normalize()
        async with AsyncSessionLocal() as db:
            return await save_articles_to_db(db, source_name, feed_url, articles)
    except Exception as e:
        print(f"Error scraping {source_name}: {e}")
        return 0
    finally:
        await connector.close()


@shared_task(name="workers.tasks.ingest.sync_sources")
def sync_sources():
    """Sync news sources from JSON file to database."""
    print("🔄 Syncing news sources from news_sources.json...")
    result = asyncio.run(sync_news_sources())
    print(f"✅ Source sync complete: {result}")
    return result


@shared_task(name="workers.tasks.ingest.run_all_scrapers")
def run_all_scrapers():
    """The main entry point for our 15-minute automation cycle"""
    print("🚀 Background Worker: Starting news ingestion...")

    async def run_concurrently():
        # Get active sources from database (synced from JSON)
        sources = await get_active_sources()

        if not sources:
            print("⚠️ No active sources in database. Run sync_sources first.")
            return 0

        tasks = [
            async_fetch_and_save(s.name, s.feed_url)
            for s in sources
        ]
        results = await asyncio.gather(*tasks)
        return sum(results)

    total_saved = asyncio.run(run_concurrently())
    print(f"🏁 Background Cycle Complete. {total_saved} new articles added.")
    return total_saved
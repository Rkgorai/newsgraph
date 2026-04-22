import asyncio
from celery import shared_task
from app.connectors.rss import RSSConnector
from app.services.ingestion_service import save_articles_to_db
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

@shared_task(name="workers.tasks.ingest.run_all_scrapers")
def run_all_scrapers():
    """The main entry point for our 15-minute automation cycle"""
    print("🚀 Background Worker: Starting news ingestion...")
    
    sources = [
        # Indian News Sources
        {"name": "The Hindu", "url": "https://www.thehindu.com/news/national/feeder/default.rss"},
        {"name": "Times of India", "url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"},
        {"name": "NDTV", "url": "https://feeds.feedburner.com/ndtvnews-top-stories"},
        {"name": "The Indian Express", "url": "https://indianexpress.com/feed/"},

        # International Tech Sources
        {"name": "The Verge", "url": "https://www.theverge.com/rss/index.xml"},
        {"name": "TechCrunch", "url": "https://techcrunch.com/feed/"},
        {"name": "NYT Tech", "url": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"},
        {"name": "Wired", "url": "https://www.wired.com/feed/rss"}
    ]

    async def run_concurrently():
        tasks = [async_fetch_and_save(s["name"], s["url"]) for s in sources]
        results = await asyncio.gather(*tasks)
        return sum(results)

    total_saved = asyncio.run(run_concurrently())
    print(f"🏁 Background Cycle Complete. {total_saved} new articles added.")
    return total_saved
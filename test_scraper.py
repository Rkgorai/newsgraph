import asyncio
from app.connectors.rss import RSSConnector
from app.services.ingestion_service import save_articles_to_db

# Fixed the typo here:
from app.core.database import AsyncSessionLocal 

async def fetch_and_save(source_name: str, feed_url: str):
    """Fetches a feed and saves it directly to PostgreSQL."""
    connector = RSSConnector(source_name=source_name, feed_url=feed_url)
    
    try:
        # 1. Fetch from the internet
        articles = await connector.fetch_and_normalize()
        
        # 2. Save to the database (Fixed typo here too)
        async with AsyncSessionLocal() as db:
            saved_count = await save_articles_to_db(db, source_name, feed_url, articles)
            
        print(f"✅ [{source_name}] Fetched {len(articles)} -> Saved {saved_count} NEW articles to DB!")
        
    except Exception as e:
        print(f"❌ [{source_name}] Failed: {e}")
    finally:
        await connector.close()

async def main():
    print("Initializing Database Ingestion Scraper...\n")
    
    news_sources = [
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
    
    # Fire them all off at the exact same time
    tasks = [fetch_and_save(s["name"], s["url"]) for s in news_sources]
    await asyncio.gather(*tasks)
    
    print("\n🐘 Database insertion complete!")

if __name__ == "__main__":
    asyncio.run(main())
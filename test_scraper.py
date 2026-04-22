import asyncio
import os
import re
from app.connectors.rss import RSSConnector

def sanitize_filename(name: str) -> str:
    """Converts a source name like 'The Hindu' to a clean filename 'the_hindu.txt'"""
    # Lowercase and replace spaces/symbols with underscores
    clean_name = re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')
    return f"{clean_name}.txt"

async def fetch_and_save(source_name: str, feed_url: str):
    """Fetches a single feed and saves it to its own text file."""
    connector = RSSConnector(source_name=source_name, feed_url=feed_url)
    
    # Generate the file path
    filename = sanitize_filename(source_name)
    output_path = os.path.join("temp_results", filename)

    try:
        articles = await connector.fetch_and_normalize()
        
        # Write the results to this specific source's file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"--- Scraped Articles from {source_name} ---\n")
            f.write(f"Total Count: {len(articles)}\n\n")
            
            for index, article in enumerate(articles, start=1):
                f.write(f"[{index}] Headline: {article.title}\n")
                f.write(f"    Link:      {article.url}\n")
                f.write(f"    Published: {article.published_at}\n")
                f.write(f"    Content:   {str(article.content)[:150]}...\n")
                f.write("-" * 60 + "\n")
                
        print(f"✅ [{source_name}] Saved {len(articles)} articles to {output_path}")
        
    except Exception as e:
        print(f"❌ [{source_name}] Failed: {e}")
    finally:
        await connector.close()

async def main():
    print("Initializing NewsGraph Concurrent Scraper...\n")
    
    # Ensure the directory exists
    os.makedirs("temp_results", exist_ok=True)
    
    # Target Indian News Sources
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
    
    print("\n📁 All downloads complete! Check the 'temp_results' folder to see your files.")

if __name__ == "__main__":
    asyncio.run(main())
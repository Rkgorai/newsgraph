from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
import trafilatura  # <--- New Import

from app.models.source import NewsSource
from app.models.article import Article
from app.schemas.article import RawArticle

def extract_full_text(url: str) -> str:
    """Visits the URL and extracts the main article body."""
    try:
        downloaded = trafilatura.fetch_url(url)
        if downloaded:
            # extract() returns clean text, or None if it fails
            return trafilatura.extract(downloaded) or ""
    except Exception as e:
        print(f"⚠️ Failed to deep scrape {url}: {e}")
    return ""

async def save_articles_to_db(
    db: AsyncSession, 
    source_name: str, 
    feed_url: str, 
    raw_articles: List[RawArticle]
) -> int:
    # 1. Get or Create the NewsSource
    result = await db.execute(select(NewsSource).where(NewsSource.name == source_name))
    source = result.scalars().first()
    
    if not source:
        source = NewsSource(name=source_name, feed_url=feed_url)
        db.add(source)
        await db.commit()
        await db.refresh(source)
        
    # 2. Filter out articles we already have
    urls = [str(article.url) for article in raw_articles]
    if not urls:
        return 0
        
    existing_result = await db.execute(select(Article.url).where(Article.url.in_(urls)))
    existing_urls = set(existing_result.scalars().all())
    
    # 3. Insert new articles
    new_articles = []
    for raw in raw_articles:
        if str(raw.url) not in existing_urls:
            
            # --- THE CHANGE STARTS HERE ---
            final_content = raw.content
            
            # If RSS content is missing, go get the full text
            if not final_content or len(final_content) < 50:
                print(f"🔍 Deep scraping for: {raw.title}")
                final_content = extract_full_text(str(raw.url))
            # --- THE CHANGE ENDS HERE ---

            new_article = Article(
                source_id=source.id,
                title=raw.title,
                content=final_content, # Now potentially full-text!
                url=str(raw.url),
                author=raw.author,
                published_at=raw.published_at,
            )
            new_articles.append(new_article)
            
    # 4. Save to PostgreSQL
    if new_articles:
        db.add_all(new_articles)
        await db.commit()
        
    return len(new_articles)
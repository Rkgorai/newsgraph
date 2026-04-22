from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List

from app.models.source import NewsSource
from app.models.article import Article
from app.schemas.article import RawArticle

async def save_articles_to_db(
    db: AsyncSession, 
    source_name: str, 
    feed_url: str, 
    raw_articles: List[RawArticle]
) -> int:
    """Saves articles to the database and skips duplicates."""
    
    # 1. Get or Create the NewsSource
    result = await db.execute(select(NewsSource).where(NewsSource.name == source_name))
    source = result.scalars().first()
    
    if not source:
        source = NewsSource(name=source_name, feed_url=feed_url)
        db.add(source)
        await db.commit()
        await db.refresh(source)
        
    # 2. Filter out articles we already have (URL Deduplication)
    urls = [str(article.url) for article in raw_articles]
    if not urls:
        return 0
        
    existing_result = await db.execute(select(Article.url).where(Article.url.in_(urls)))
    existing_urls = set(existing_result.scalars().all())
    
    # 3. Insert new articles
    new_articles = []
    for raw in raw_articles:
        if str(raw.url) not in existing_urls:
            new_article = Article(
                source_id=source.id,
                title=raw.title,
                content=raw.content,
                url=str(raw.url),
                author=raw.author,
                published_at=raw.published_at,
            )
            new_articles.append(new_article)
            
    # 4. Save to PostgreSQL
    if new_articles:
        db.add_all(new_articles)
        await db.commit()
        
    # Return how many *new* articles were successfully saved
    return len(new_articles)
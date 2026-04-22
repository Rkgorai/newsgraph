from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from typing import List

from app.core.database import AsyncSessionLocal  # Ensure this matches your session variable name
from app.models.article import Article
from app.schemas.article import FeedResponse

# This is the 'router' variable your main.py is looking for
router = APIRouter()

# Dependency to get a database session
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.get("/", response_model=FeedResponse)
async def get_feed(
    limit: int = Query(20, gt=0, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch a paginated list of news articles, 
    ordered by the most recently published.
    """
    # 1. Build the query with a join to get Source details
    query = (
        select(Article)
        .options(joinedload(Article.source))
        .order_by(Article.published_at.desc())
        .offset(offset)
        .limit(limit)
    )
    
    result = await db.execute(query)
    articles = result.scalars().all()

    # DEBUG: Check the first article's content in the console
    if articles:
        print(f"DEBUG: First article content length: {len(articles[0].content or '')}")
    
    # 2. Get total count for the 'total' field in response
    # In a production app, you might use a separate count() query for performance
    count_query = select(Article.id)
    count_result = await db.execute(count_query)
    total_count = len(count_result.scalars().all())

    return {
        "total": total_count, 
        "articles": articles
    }
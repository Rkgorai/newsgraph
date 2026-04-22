from pydantic import BaseModel, HttpUrl, Field
from uuid import UUID
from datetime import datetime
from typing import Optional, List

# --- SCRAPER MODELS (Phase 2) ---
class RawArticle(BaseModel):
    """Schema for the initial fetch from RSS feeds"""
    title: str
    content: str
    url: str
    author: Optional[str] = None
    published_at: datetime
    image_url: Optional[str] = None

# --- API RESPONSE MODELS (Phase 3) ---
class SourceRead(BaseModel):
    id: UUID
    name: str

    class Config:
        from_attributes = True

class ArticleRead(BaseModel):
    id: UUID
    title: str
    content: Optional[str] = ""  # <--- Add this line
    url: str
    author: Optional[str] = None
    published_at: datetime
    source: SourceRead

    class Config:
        from_attributes = True

class FeedResponse(BaseModel):
    total: int
    articles: List[ArticleRead]
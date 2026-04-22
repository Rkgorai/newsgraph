from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional

class RawArticle(BaseModel):
    """The standard format for all incoming news articles, regardless of source."""
    title: str
    content: Optional[str] = None
    url: HttpUrl
    source_name: str
    published_at: datetime
    author: Optional[str] = None
    
    # We will generate these hashes later in the deduplication engine
    url_hash: Optional[str] = None 
    content_hash: Optional[str] = None
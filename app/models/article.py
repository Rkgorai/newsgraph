import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("news_sources.id"), nullable=False)
    
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)
    url = Column(String, nullable=False, unique=True)
    author = Column(String, nullable=True)
    
    published_at = Column(DateTime(timezone=True), nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Fast-lookup columns for exact deduplication (Phase 4)
    url_hash = Column(String(64), nullable=True, index=True)
    content_hash = Column(String(64), nullable=True, index=True)

    # Link back to the NewsSource table
    source = relationship("NewsSource", back_populates="articles")
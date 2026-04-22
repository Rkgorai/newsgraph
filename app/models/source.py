import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base

class NewsSource(Base):
    __tablename__ = "news_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    feed_url = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    # Establish a relationship so a Source can have many Articles
    articles = relationship("Article", back_populates="source", cascade="all, delete-orphan")
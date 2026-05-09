import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Boolean, ARRAY, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class MarketSignal(Base):
    __tablename__ = "market_signals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(
        UUID(as_uuid=True), nullable=False
    )  # FK to articles, defined in migration
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )

    # Core signal
    sentiment = Column(String(16), nullable=False)  # positive / negative / neutral
    sentiment_score = Column(Float, nullable=False)  # FinBERT confidence [0, 1]
    event_type = Column(String(64), nullable=True)  # earnings_beat, layoffs, etc.
    event_confidence = Column(Float, nullable=True)  # classifier confidence [0, 1]
    impact_score = Column(Float, nullable=False)  # composite score [0, 1]
    time_horizon = Column(String(16), nullable=True)  # short_term / medium_term / long_term

    # Multi-source aggregation
    confidence_score = Column(Float, default=0.0)  # grows with mention_count
    mention_count = Column(Float, default=1)
    source_ids = Column(ARRAY(UUID), nullable=True)  # all contributing article IDs

    story_id = Column(UUID, nullable=True)  # FK to topics.id (story cluster)
    is_aggregated = Column(Boolean, default=False)
    published_at = Column(DateTime(timezone=True), nullable=False)
    analyzed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
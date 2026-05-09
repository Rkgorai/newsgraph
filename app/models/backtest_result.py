import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True
    )
    event_type = Column(String(64), nullable=True)
    sentiment = Column(String(16), nullable=True)

    # Average returns
    avg_return_1d = Column(Float, nullable=True)  # (close[+1] - close[0]) / close[0], averaged
    avg_return_3d = Column(Float, nullable=True)
    avg_return_7d = Column(Float, nullable=True)

    # Correlations
    sentiment_return_corr = Column(Float, nullable=True)  # Pearson(sentiment_score, return_1d)
    impact_return_corr = Column(Float, nullable=True)  # Pearson(impact_score, return_7d)

    # Metadata
    sample_count = Column(Integer, nullable=True)
    window_days = Column(Integer, default=90)
    computed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, ARRAY, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.core.database import Base


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)  # "Tesla, Inc."
    ticker = Column(String(16), nullable=False, unique=True)  # "TSLA"
    exchange = Column(String(16), nullable=True)  # "NASDAQ", "NYSE"
    sector = Column(String(64), nullable=True)
    aliases = Column(ARRAY(String), nullable=True)  # ["Tesla", "Tesla Motors", "TSLA"]
    is_tracked = Column(Boolean, default=True)
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
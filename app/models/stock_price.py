import uuid
from datetime import date as dt_date
from sqlalchemy import Column, String, Numeric, BigInteger, UniqueConstraint, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class StockPrice(Base):
    __tablename__ = "stock_prices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False
    )
    date = Column(Date, nullable=False)
    open = Column(Numeric(12, 4), nullable=True)
    high = Column(Numeric(12, 4), nullable=True)
    low = Column(Numeric(12, 4), nullable=True)
    close = Column(Numeric(12, 4), nullable=True)
    adj_close = Column(Numeric(12, 4), nullable=True)
    volume = Column(BigInteger, nullable=True)
    source = Column(String(32), default="yahoo")  # "yahoo" or "polygon"

    # Unique constraint for upsert
    __table_args__ = (UniqueConstraint("company_id", "date", name="uq_stock_price_company_date"),)
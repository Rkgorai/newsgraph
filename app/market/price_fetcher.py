"""
OHLC price fetcher using yfinance with rate limiting.
"""
import time
from datetime import date, timedelta
from typing import Optional
import yfinance as yf

from app.core.database import AsyncSessionLocal
from app.models.stock_price import StockPrice
from sqlalchemy import select


# Rate limit: max requests per second
MAX_REQUESTS_PER_SECOND = 2
REQUEST_INTERVAL = 1.0 / MAX_REQUESTS_PER_SECOND

_last_request_time = 0.0


def _rate_limit():
    """Apply rate limiting to respect API limits."""
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()


def fetch_ohlc(ticker: str, target_date: Optional[date] = None) -> Optional[dict]:
    """
    Fetch OHLC data for a single ticker and date.

    Args:
        ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")
        target_date: Date to fetch. Defaults to yesterday.

    Returns:
        Dict with keys: date, open, high, low, close, adj_close, volume, source
        Returns None if fetch fails.
    """
    if target_date is None:
        target_date = date.today() - timedelta(days=1)

    _rate_limit()

    try:
        # yfinance expects period, not specific date, so we fetch a range
        # Fetch 7 days to ensure we get the target date
        start_date = target_date - timedelta(days=7)
        end_date = target_date + timedelta(days=1)

        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            return None

        # Find the row matching target_date
        for idx, row in hist.iterrows():
            if idx.date() == target_date:
                return {
                    "date": target_date,
                    "open": float(row["Open"]) if not pd.isna(row["Open"]) else None,
                    "high": float(row["High"]) if not pd.isna(row["High"]) else None,
                    "low": float(row["Low"]) if not pd.isna(row["Low"]) else None,
                    "close": float(row["Close"]) if not pd.isna(row["Close"]) else None,
                    "adj_close": float(row["Close"]) if not pd.isna(row["Close"]) else None,  # Use close for adj
                    "volume": int(row["Volume"]) if not pd.isna(row["Volume"]) else None,
                    "source": "yahoo",
                }

        # If exact date not found, use the last available date in range
        if not hist.empty:
            last_row = hist.iloc[-1]
            last_date = last_row.name.date()
            return {
                "date": last_date,
                "open": float(last_row["Open"]) if not pd.isna(last_row["Open"]) else None,
                "high": float(last_row["High"]) if not pd.isna(last_row["High"]) else None,
                "low": float(last_row["Low"]) if not pd.isna(last_row["Low"]) else None,
                "close": float(last_row["Close"]) if not pd.isna(last_row["Close"]) else None,
                "adj_close": float(last_row["Close"]) if not pd.isna(last_row["Close"]) else None,
                "volume": int(last_row["Volume"]) if not pd.isna(last_row["Volume"]) else None,
                "source": "yahoo",
            }

        return None

    except Exception as e:
        print(f"⚠️ Failed to fetch {ticker}: {e}")
        return None


async def fetch_and_upsert_prices(
    ticker: str,
    company_id: str,
    target_date: Optional[date] = None
) -> bool:
    """
    Fetch OHLC data and upsert into the database.

    Args:
        ticker: Stock ticker symbol
        company_id: UUID of the company in our database
        target_date: Date to fetch. Defaults to yesterday.

    Returns:
        True if successful, False otherwise
    """
    ohlc_data = fetch_ohlc(ticker, target_date)

    if not ohlc_data:
        return False

    async with AsyncSessionLocal() as db:
        # Check if exists
        result = await db.execute(
            select(StockPrice).where(
                StockPrice.company_id == company_id,
                StockPrice.date == ohlc_data["date"]
            )
        )
        existing = result.scalars().first()

        if existing:
            # Update existing
            existing.open = ohlc_data["open"]
            existing.high = ohlc_data["high"]
            existing.low = ohlc_data["low"]
            existing.close = ohlc_data["close"]
            existing.adj_close = ohlc_data["adj_close"]
            existing.volume = ohlc_data["volume"]
            existing.source = ohlc_data["source"]
        else:
            # Insert new
            price = StockPrice(
                company_id=company_id,
                date=ohlc_data["date"],
                open=ohlc_data["open"],
                high=ohlc_data["high"],
                low=ohlc_data["low"],
                close=ohlc_data["close"],
                adj_close=ohlc_data["adj_close"],
                volume=ohlc_data["volume"],
                source=ohlc_data["source"],
            )
            db.add(price)

        await db.commit()

    return True


# Import pandas for NaN checking
import pandas as pd
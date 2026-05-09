"""
Celery task to fetch OHLC prices for all tracked companies.
Runs daily at 01:00 UTC.
"""
import asyncio
from datetime import date, timedelta
from celery import shared_task

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.models.company import Company
from sqlalchemy import select, func


async def _fetch_all_prices():
    """Async helper to fetch prices for all tracked companies."""
    yesterday = date.today() - timedelta(days=1)

    async with AsyncSessionLocal() as db:
        # Get all tracked companies
        result = await db.execute(
            select(Company).where(Company.is_tracked == True)
        )
        companies = result.scalars().all()

        if not companies:
            print("⚠️ No tracked companies found. Run company seeding first.")
            return

        print(f"📈 Fetching prices for {len(companies)} companies...")

        # Import here to avoid circular imports
        from app.market.price_fetcher import fetch_and_upsert_prices

        success_count = 0
        failure_count = 0

        for company in companies:
            try:
                success = await fetch_and_upsert_prices(
                    ticker=company.ticker,
                    company_id=company.id,
                    target_date=yesterday
                )
                if success:
                    success_count += 1
                else:
                    failure_count += 1
            except Exception as e:
                print(f"⚠️ Failed to fetch {company.ticker}: {e}")
                failure_count += 1

        print(f"✅ Price fetch complete: {success_count} success, {failure_count} failed")


@shared_task(name="workers.tasks.market.fetch_prices.fetch_daily_prices")
def fetch_daily_prices():
    """
    Fetch daily OHLC prices for all tracked companies.

    Scheduled: Daily at 01:00 UTC via Celery Beat
    """
    asyncio.run(_fetch_all_prices())
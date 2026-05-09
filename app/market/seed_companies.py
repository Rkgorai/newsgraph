"""
Seed companies table with initial data.
Run this to populate the database with tracked companies.
"""
import asyncio
from datetime import timezone
from datetime import datetime

from app.core.database import AsyncSessionLocal
from app.models.company import Company
from app.market.ticker_map import load_companies


# Sample companies for initial seeding (subset of S&P 500 for testing)
# In production, this would be loaded from a CSV file
SAMPLE_COMPANIES = [
    {
        "ticker": "AAPL",
        "name": "Apple Inc.",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "aliases": ["Apple", "Apple Computer", "AAPL"],
    },
    {
        "ticker": "MSFT",
        "name": "Microsoft Corporation",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "aliases": ["Microsoft", "MSFT"],
    },
    {
        "ticker": "GOOGL",
        "name": "Alphabet Inc.",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "aliases": ["Google", "Alphabet", "GOOG"],
    },
    {
        "ticker": "AMZN",
        "name": "Amazon.com Inc.",
        "exchange": "NASDAQ",
        "sector": "Consumer Cyclical",
        "aliases": ["Amazon", "AMZN"],
    },
    {
        "ticker": "NVDA",
        "name": "NVIDIA Corporation",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "aliases": ["Nvidia", "NVIDIA", "NVDA"],
    },
    {
        "ticker": "META",
        "name": "Meta Platforms Inc.",
        "exchange": "NASDAQ",
        "sector": "Technology",
        "aliases": ["Meta", "Facebook", "FB"],
    },
    {
        "ticker": "TSLA",
        "name": "Tesla Inc.",
        "exchange": "NASDAQ",
        "sector": "Consumer Cyclical",
        "aliases": ["Tesla", "Tesla Motors", "TSLA"],
    },
    {
        "ticker": "BRK.B",
        "name": "Berkshire Hathaway Inc.",
        "exchange": "NYSE",
        "sector": "Financial",
        "aliases": ["Berkshire", "BRK", "BRK.A"],
    },
    {
        "ticker": "JPM",
        "name": "JPMorgan Chase & Co.",
        "exchange": "NYSE",
        "sector": "Financial",
        "aliases": ["JPMorgan", "JPM", "Chase"],
    },
    {
        "ticker": "V",
        "name": "Visa Inc.",
        "exchange": "NYSE",
        "sector": "Financial",
        "aliases": ["Visa", "V"],
    },
    {
        "ticker": "JNJ",
        "name": "Johnson & Johnson",
        "exchange": "NYSE",
        "sector": "Healthcare",
        "aliases": ["Johnson & Johnson", "J&J", "JNJ"],
    },
    {
        "ticker": "WMT",
        "name": "Walmart Inc.",
        "exchange": "NYSE",
        "sector": "Consumer Defensive",
        "aliases": ["Walmart", "WMT"],
    },
    {
        "ticker": "PG",
        "name": "Procter & Gamble Co.",
        "exchange": "NYSE",
        "sector": "Consumer Defensive",
        "aliases": ["Procter & Gamble", "P&G", "PG"],
    },
    {
        "ticker": "MA",
        "name": "Mastercard Inc.",
        "exchange": "NYSE",
        "sector": "Financial",
        "aliases": ["Mastercard", "MA"],
    },
    {
        "ticker": "UNH",
        "name": "UnitedHealth Group Inc.",
        "exchange": "NYSE",
        "sector": "Healthcare",
        "aliases": ["UnitedHealth", "UNH"],
    },
    {
        "ticker": "HD",
        "name": "The Home Depot Inc.",
        "exchange": "NYSE",
        "sector": "Consumer Cyclical",
        "aliases": ["Home Depot", "HD"],
    },
    {
        "ticker": "DIS",
        "name": "The Walt Disney Company",
        "exchange": "NYSE",
        "sector": "Communication Services",
        "aliases": ["Disney", "DIS"],
    },
    {
        "ticker": "BAC",
        "name": "Bank of America Corporation",
        "exchange": "NYSE",
        "sector": "Financial",
        "aliases": ["Bank of America", "BAC"],
    },
    {
        "ticker": "XOM",
        "name": "Exxon Mobil Corporation",
        "exchange": "NYSE",
        "sector": "Energy",
        "aliases": ["Exxon", "ExxonMobil", "XOM"],
    },
    {
        "ticker": "PFE",
        "name": "Pfizer Inc.",
        "exchange": "NYSE",
        "sector": "Healthcare",
        "aliases": ["Pfizer", "PFE"],
    },
]


async def seed_companies():
    """Seed the companies table with initial data."""
    async with AsyncSessionLocal() as db:
        # Check if companies already exist
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Company.id)))
        count = result.scalar()

        if count > 0:
            print(f"⚠️ Companies table already has {count} entries. Skipping seed.")
            return

        # Add companies
        companies = []
        for data in SAMPLE_COMPANIES:
            company = Company(
                name=data["name"],
                ticker=data["ticker"],
                exchange=data.get("exchange"),
                sector=data.get("sector"),
                aliases=data.get("aliases", []),
                is_tracked=True,
                created_at=datetime.now(timezone.utc),
            )
            companies.append(company)

        db.add_all(companies)
        await db.commit()

        print(f"✅ Seeded {len(companies)} companies")

        # Load into ticker_map cache
        load_companies(SAMPLE_COMPANIES)
        print("✅ Loaded companies into ticker_map cache")


if __name__ == "__main__":
    asyncio.run(seed_companies())
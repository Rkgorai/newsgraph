# NewsGraph — Market Intelligence Platform

A news aggregation and enrichment platform that extracts financial signals from news articles, correlates them with stock prices, and provides market intelligence through a REST API.

---

## 📋 Overview

NewsGraph is designed to:

1. **Ingest news** from multiple RSS sources (Indian and International)
2. **Extract full article content** using Trafilatura
3. **Enrich with market intelligence** using NLP/ML (Phase 2+):
   - Named Entity Recognition (NER) for company detection
   - Sentiment analysis (FinBERT)
   - Event classification (earnings, layoffs, acquisitions, etc.)
   - Impact scoring
4. **Store OHLC price data** for backtesting (yfinance)
5. **Correlate signals with price movements** to evaluate signal quality
6. **Serve market insights** via REST API

---

## 🏗 Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  RSS Feeds  │────▶│  Celery     │────▶│ PostgreSQL  │
│  (20+ srcs) │     │  Workers    │     │  (Articles) │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                   │
                    ┌──────▼──────┐      ┌──────▼──────┐
                    │   Market    │      │   Market    │
                    │ Intelligence│◀─────│  Intelligence
                    │  (Phase 2) │      │   (Phase 2) │
                    └──────┬──────┘      └──────┬──────┘
                           │                   │
                    ┌──────▼──────┐      ┌──────▼──────┐
                    │ Stock Prices│      │Market Signals
                    │   (yfinance)│      │   (Signals) │
                    └─────────────┘      └─────────────┘
                                               │
                                        ┌──────▼──────┐
                                        │  REST API   │
                                        │  /market/*  │
                                        └─────────────┘
```

### Tech Stack

| Component | Technology |
|-----------|------------|
| Web Framework | FastAPI |
| Database | PostgreSQL (with pgvector) |
| Task Queue | Celery + Redis |
| NLP/ML | spaCy, FinBERT, HuggingFace |
| Price Data | yfinance |
| Search | Elasticsearch |
| ORM | SQLAlchemy (async) |

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Redis (included in docker-compose)

### 2. Start Infrastructure

```bash
# Start database, redis, elasticsearch
docker compose up -d

# Verify services are running
docker ps
```

### 3. Install Dependencies

```bash
# Creates virtual environment and installs packages
uv sync
```

### 4. Run Migrations

```bash
uv run alembic upgrade head
```

### 5. Seed Initial Data

```bash
# Seed news sources from JSON
uv run python -c "import asyncio; from app.services.source_service import sync_news_sources; print(asyncio.run(sync_news_sources()))"

# Seed sample companies for market intelligence
uv run python -c "import asyncio; from app.market.seed_companies import seed_companies; asyncio.run(seed_companies())"
```

### 6. Start the Server

```bash
# Terminal 1: API server
uv run uvicorn app.main:app --reload

# Terminal 2: Celery worker (optional, for background tasks)
uv run celery -A workers.celery_app worker --loglevel=info

# Terminal 3: Celery beat (optional, for scheduled tasks)
uv run celery -A workers.celery_app beat
```

### 7. Ingest News

```bash
# Scrape all sources
uv run python test_scraper.py

# Or with limit for testing
uv run python test_scraper.py --limit 5
```

---

## 📖 Usage Guide

### News Source Management

Sources are configured in `news_sources.json`. To add/modify/remove sources:

1. Edit `news_sources.json`
2. Run sync to update database:
   ```bash
   uv run python -c "import asyncio; from app.services.source_service import sync_news_sources; print(asyncio.run(sync_news_sources()))"
   ```

### API Endpoints

Once the server is running:

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/feed` | Latest news articles |
| `GET /api/v1/health` | Health check |
| `GET /api/v1/market/signals` | Market signals (Phase 2+) |
| `GET /api/v1/market/company/{ticker}` | Company profile + signals |
| `GET /api/v1/market/feed` | High-impact signals (24h) |
| `GET /api/v1/market/backtest` | Backtest correlations |

### Database Queries

```bash
# Count articles
docker exec newsgraph_db psql -U postgres -d newsgraph -c "SELECT COUNT(*) FROM articles;"

# List sources with article counts
docker exec newsgraph_db psql -U postgres -d newsgraph -c "SELECT ns.name, COUNT(*) FROM articles a JOIN news_sources ns ON a.source_id = ns.id GROUP BY ns.name;"

# List companies
docker exec newsgraph_db psql -U postgres -d newsgraph -c "SELECT ticker, name, sector FROM companies;"

# Check stock prices
docker exec newsgraph_db psql -U postgres -d newsgraph -c "SELECT c.ticker, sp.date, sp.close FROM stock_prices sp JOIN companies c ON sp.company_id = c.id;"
```

---

## 📁 Project Structure

```
newsgraph/
├── app/
│   ├── api/v1/              # REST API endpoints
│   │   ├── feed.py          # /feed endpoint
│   │   ├── health.py        # /health endpoint
│   │   └── market.py       # /market endpoints (Phase 2+)
│   │
│   ├── connectors/          # Data source connectors
│   │   └── rss.py          # RSS feed scraper
│   │
│   ├── core/               # Core infrastructure
│   │   ├── config.py       # Settings/configuration
│   │   └── database.py     # SQLAlchemy setup
│   │
│   ├── market/             # Market Intelligence Layer (Phase 2+)
│   │   ├── __init__.py
│   │   ├── filter.py       # Finance relevance filter
│   │   ├── ner_service.py  # NER + TickerResolver
│   │   ├── sentiment_service.py  # FinBERT sentiment
│   │   ├── event_service.py     # Event classification
│   │   ├── scoring_service.py   # Impact scoring
│   │   ├── aggregation_service.py  # Signal aggregation
│   │   ├── backtest_service.py    # Backtesting engine
│   │   ├── price_fetcher.py      # yfinance OHLC fetch
│   │   ├── ticker_map.py         # Company→ticker lookup
│   │   └── seed_companies.py     # Company seeding
│   │
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── article.py      # Article model
│   │   ├── source.py       # NewsSource model
│   │   ├── company.py      # Company model
│   │   ├── market_signal.py # MarketSignal model
│   │   ├── stock_price.py  # StockPrice model
│   │   └── backtest_result.py # BacktestResult model
│   │
│   ├── schemas/            # Pydantic schemas
│   │   ├── article.py      # Article schemas
│   │   └── market.py       # Market schemas
│   │
│   └── services/           # Business logic
│       ├── ingestion_service.py  # Article save logic
│       └── source_service.py     # Source management
│
├── workers/                # Celery tasks
│   ├── celery_app.py       # Celery configuration
│   └── tasks/
│       ├── ingest.py       # News ingestion tasks
│       └── market/
│           ├── fetch_prices.py  # Daily price fetch (01:00 UTC)
│           └── run_backtest.py # Nightly backtest (02:30 UTC)
│
├── alembic/                # Database migrations
│   ├── versions/
│   │   ├── 4e17c8345172_add_news_sources_and_articles_tables.py
│   │   └── xxxx_add_market_tables.py
│   └── env.py
│
├── news_sources.json       # News source configuration
├── test_scraper.py         # Test ingestion script
├── docker-compose.yml      # Docker services
├── pyproject.toml          # Python dependencies
└── alembic.ini            # Alembic configuration
```

---

## 🔄 Workflow

### Phase 1: Data Foundation (Complete ✅)

1. **News Ingestion**: Fetch articles from RSS feeds
2. **Content Extraction**: Use Trafilatura for full-text
3. **Company Registry**: Seed 20 sample companies (S&P 500 subset)
4. **Price Fetching**: Daily OHLC from yfinance

### Phase 2: NLP Services (In Progress 🚧)

- [ ] **Finance Relevance Filter**: Pre-filter non-financial articles
- [ ] **NER Engine**: spaCy + TickerResolver for company detection
- [ ] **Sentiment Analysis**: FinBERT with VADER fallback
- [ ] **Event Classification**: Zero-shot BART for event types

### Phase 3: MVP (Planned 📋)

- [ ] **Impact Scoring**: Formula-based signal scoring
- [ ] **Signal Aggregation**: Multi-source confidence
- [ ] **Market API**: /market/signals, /market/company/{ticker}
- [ ] **Redis Caching**: For API performance

### Phase 4-6: Advanced (Planned 📋)

- [ ] **Story Clustering**: Link signals to topics
- [ ] **Backtesting Engine**: Pearson correlations
- [ ] **Observability**: Prometheus metrics
- [ ] **Circuit Breakers**: yfinance fallback

---

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run specific test
uv run pytest test_scraper.py -v
```

---

## ⚙️ Configuration

Environment variables (can be set in `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_USER` | postgres | Database user |
| `POSTGRES_PASSWORD` | password | Database password |
| `POSTGRES_SERVER` | localhost | Database host |
| `POSTGRES_PORT` | 5432 | Database port |
| `POSTGRES_DB` | newsgraph | Database name |
| `REDIS_URL` | redis://localhost:6379/0 | Redis connection |

---

## 📈 Current Status

| Component | Status |
|-----------|--------|
| News Ingestion | ✅ Working |
| Deep Content Extraction | ✅ Working |
| Source Management (JSON) | ✅ Working |
| PostgreSQL + Redis | ✅ Working |
| Celery Tasks | ✅ Working |
| Company Seeding | ✅ Working (20 companies) |
| Price Fetching | ✅ Working |
| Market Signals | ❌ Not implemented |
| NER/Sentiment/Event | ❌ Not implemented |
| Market API | ❌ Not implemented |
| Backtesting | ❌ Not implemented |

---

## 🚢 Deployment

For production deployment:

1. Set environment variables in `.env`
2. Use proper PostgreSQL credentials
3. Configure Redis with password
4. Set up proper Celery workers with concurrency limits
5. Add reverse proxy (nginx) for API
6. Set up monitoring (Prometheus + Grafana)

---

## 📝 License

MIT License

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test
4. Submit a pull request

---

## 📚 References

- [FastAPI](https://fastapi.tiangolo.com/)
- [Celery](https://docs.celeryproject.org/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Trafilatura](https://trafilatura.readthedocs.io/)
- [yfinance](https://pypi.org/project/yfinance/)
- [FinBERT](https://huggingface.co/ProsusAI/finbert)
- [spaCy](https://spacy.io/)
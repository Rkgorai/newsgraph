"""
Ticker mapping service: company name/alias → ticker lookup with fuzzy matching.
"""
from typing import Optional
from rapidfuzz import fuzz, process


# In-memory cache for company lookup
# Format: {name_lower: ticker}
_name_to_ticker: dict[str, str] = {}

# Format: {ticker: {"name": str, "aliases": list[str]}}
_ticker_data: dict[str, dict] = {}

# Fuzzy match threshold
FUZZY_THRESHOLD = 85


def load_companies(companies: list[dict]) -> None:
    """
    Load company data into the lookup cache.

    Args:
        companies: List of dicts with keys: ticker, name, aliases (list)
    """
    global _name_to_ticker, _ticker_data

    _name_to_ticker.clear()
    _ticker_data.clear()

    for company in companies:
        ticker = company["ticker"].upper()
        name = company["name"]
        aliases = company.get("aliases", [])

        _ticker_data[ticker] = {"name": name, "aliases": aliases}

        # Add canonical name (lowercase)
        _name_to_ticker[name.lower()] = ticker

        # Add all aliases
        for alias in aliases:
            _name_to_ticker[alias.lower()] = ticker


def resolve_ticker(company_name: str) -> Optional[str]:
    """
    Resolve a company name to its ticker symbol.

    First tries exact match (case-insensitive), then fuzzy matching.

    Args:
        company_name: Company name or alias to resolve

    Returns:
        Ticker symbol if found, None otherwise
    """
    if not company_name:
        return None

    name_lower = company_name.lower()

    # 1. Exact match on name or aliases
    if name_lower in _name_to_ticker:
        return _name_to_ticker[name_lower]

    # 2. Fuzzy match against all known names
    # Get all known names for fuzzy matching
    known_names = list(_name_to_ticker.keys())

    if not known_names:
        return None

    # Use rapidfuzz to find best match
    result = process.extractOne(
        name_lower,
        known_names,
        scorer=fuzz.WRatio,
        score_cutoff=FUZZY_THRESHOLD
    )

    if result:
        matched_name, score, _ = result
        return _name_to_ticker[matched_name]

    return None


def get_ticker_info(ticker: str) -> Optional[dict]:
    """Get company info for a ticker."""
    return _ticker_data.get(ticker.upper())


def get_all_tickers() -> list[str]:
    """Get list of all tracked tickers."""
    return list(_ticker_data.keys())


def is_tracked(company_name: str) -> bool:
    """Check if a company name resolves to a tracked ticker."""
    return resolve_ticker(company_name) is not None
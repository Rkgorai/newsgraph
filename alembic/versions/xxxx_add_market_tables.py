"""Add market tables (companies, market_signals, stock_prices, backtest_results)

Revision ID: xxxx
Revises: 4e17c8345172
Create Date: 2026-05-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'xxxx'
down_revision: Union[str, Sequence[str], None] = '4e17c8345172'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('ticker', sa.String(length=16), nullable=False),
        sa.Column('exchange', sa.String(length=16), nullable=True),
        sa.Column('sector', sa.String(length=64), nullable=True),
        sa.Column('aliases', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('is_tracked', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ticker')
    )
    op.create_index('ix_companies_ticker', 'companies', ['ticker'], unique=False)
    op.create_index('ix_companies_aliases', 'companies', ['aliases'], unique=False, postgresql_using='gin')

    # Market Signals table
    op.create_table(
        'market_signals',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('article_id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('sentiment', sa.String(length=16), nullable=False),
        sa.Column('sentiment_score', sa.Float(), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=True),
        sa.Column('event_confidence', sa.Float(), nullable=True),
        sa.Column('impact_score', sa.Float(), nullable=False),
        sa.Column('time_horizon', sa.String(length=16), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('mention_count', sa.Float(), nullable=True),
        sa.Column('source_ids', postgresql.ARRAY(sa.UUID()), nullable=True),
        sa.Column('story_id', sa.UUID(), nullable=True),
        sa.Column('is_aggregated', sa.Boolean(), nullable=True),
        sa.Column('published_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('analyzed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_market_signals_company_published', 'market_signals', ['company_id', sa.text('published_at DESC')], unique=False)
    op.create_index('ix_market_signals_event_type', 'market_signals', ['event_type'], unique=False)
    op.create_index('ix_market_signals_impact_score', 'market_signals', ['impact_score'], unique=False)
    op.create_index('ix_market_signals_story_id', 'market_signals', ['story_id'], unique=False)

    # Stock Prices table
    op.create_table(
        'stock_prices',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('open', sa.Numeric(12, 4), nullable=True),
        sa.Column('high', sa.Numeric(12, 4), nullable=True),
        sa.Column('low', sa.Numeric(12, 4), nullable=True),
        sa.Column('close', sa.Numeric(12, 4), nullable=True),
        sa.Column('adj_close', sa.Numeric(12, 4), nullable=True),
        sa.Column('volume', sa.BigInteger(), nullable=True),
        sa.Column('source', sa.String(length=32), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_id', 'date', name='uq_stock_price_company_date')
    )
    op.create_index('ix_stock_prices_company_date', 'stock_prices', ['company_id', sa.text('date DESC')], unique=False)

    # Backtest Results table
    op.create_table(
        'backtest_results',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('company_id', sa.UUID(), nullable=True),
        sa.Column('event_type', sa.String(length=64), nullable=True),
        sa.Column('sentiment', sa.String(length=16), nullable=True),
        sa.Column('avg_return_1d', sa.Float(), nullable=True),
        sa.Column('avg_return_3d', sa.Float(), nullable=True),
        sa.Column('avg_return_7d', sa.Float(), nullable=True),
        sa.Column('sentiment_return_corr', sa.Float(), nullable=True),
        sa.Column('impact_return_corr', sa.Float(), nullable=True),
        sa.Column('sample_count', sa.Integer(), nullable=True),
        sa.Column('window_days', sa.Integer(), nullable=True),
        sa.Column('computed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('backtest_results')
    op.drop_table('stock_prices')
    op.drop_table('market_signals')
    op.drop_table('companies')
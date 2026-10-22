"""Create the initial articles table.

Revision ID: 20260903_0001
Revises:
Create Date: 2026-09-03
"""

from collections.abc import Sequence
from datetime import UTC, date, datetime

import sqlalchemy as sa
from alembic import op


revision: str = "20260903_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "articles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("summary", sa.String(length=500), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("published", sa.Boolean(), nullable=False),
        sa.Column("published_on", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_articles_slug", "articles", ["slug"], unique=True)
    op.create_index("ix_articles_published", "articles", ["published"], unique=False)
    articles = sa.table(
        "articles",
        sa.column("id", sa.Integer),
        sa.column("slug", sa.String),
        sa.column("title", sa.String),
        sa.column("summary", sa.String),
        sa.column("content", sa.Text),
        sa.column("published", sa.Boolean),
        sa.column("published_on", sa.Date),
        sa.column("created_at", sa.DateTime),
    )
    op.bulk_insert(
        articles,
        [
            {
                "id": 1,
                "slug": "t-1",
                "title": "婕旂ず",
                "summary": "鏉＄洰1，無指向",
                "content": "wwww",
                "published": True,
                "published_on": date(2026, 2, 7),
                "created_at": datetime(2026, 2, 7, tzinfo=UTC),
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_articles_published", table_name="articles")
    op.drop_index("ix_articles_slug", table_name="articles")
    op.drop_table("articles")

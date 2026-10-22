from datetime import date

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select

from app.db.models import Article
from app.db.session import get_session_factory


class ArticleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    title: str
    summary: str
    published_on: date


class ArticleDetail(ArticleSummary):
    content: str


router = APIRouter(prefix="/articles", tags=["articles"])


@router.get("", response_model=list[ArticleSummary])
def list_articles() -> list[Article]:
    with get_session_factory()() as session:
        statement = (
            select(Article)
            .where(Article.published.is_(True))
            .order_by(Article.published_on.desc(), Article.id.desc())
        )
        return list(session.scalars(statement))


@router.get("/{slug}", response_model=ArticleDetail)
def get_article(slug: str) -> Article:
    with get_session_factory()() as session:
        article = session.scalar(
            select(Article).where(
                Article.slug == slug,
                Article.published.is_(True),
            )
        )
        if article is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="article not found",
            )
        return article


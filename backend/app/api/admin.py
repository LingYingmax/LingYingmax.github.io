from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.core.auth import bearer_scheme, require_admin
from app.db.models import Article
from app.db.session import get_session_factory


class ArticleInput(BaseModel):
    slug: str = Field(min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=1, max_length=200)
    summary: str = Field(default="", max_length=500)
    content: str = ""
    published: bool = True
    published_on: date


class ArticleUpdate(BaseModel):
    slug: str | None = Field(default=None, min_length=1, max_length=120, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    summary: str | None = Field(default=None, max_length=500)
    content: str | None = None
    published: bool | None = None
    published_on: date | None = None


class ManagedArticle(ArticleInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


router = APIRouter(prefix="/admin/articles", tags=["admin"])


def admin_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    return require_admin(credentials)


@router.get("", response_model=list[ManagedArticle])
def list_managed_articles(_: str = Depends(admin_user)) -> list[Article]:
    with get_session_factory()() as session:
        return list(session.scalars(select(Article).order_by(Article.published_on.desc(), Article.id.desc())))


@router.post("", response_model=ManagedArticle, status_code=status.HTTP_201_CREATED)
def create_article(article_input: ArticleInput, _: str = Depends(admin_user)) -> Article:
    article = Article(**article_input.model_dump())
    with get_session_factory()() as session:
        session.add(article)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already exists") from error
        session.refresh(article)
        return article


@router.put("/{article_id}", response_model=ManagedArticle)
def update_article(article_id: int, article_input: ArticleUpdate, _: str = Depends(admin_user)) -> Article:
    with get_session_factory()() as session:
        article = session.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="article not found")
        for field, value in article_input.model_dump(exclude_unset=True).items():
            setattr(article, field, value)
        try:
            session.commit()
        except IntegrityError as error:
            session.rollback()
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="slug already exists") from error
        session.refresh(article)
        return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(article_id: int, _: str = Depends(admin_user)) -> None:
    with get_session_factory()() as session:
        article = session.get(Article, article_id)
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="article not found")
        session.delete(article)
        session.commit()


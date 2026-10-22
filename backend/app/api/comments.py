from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.core.auth import bearer_scheme, require_user
from app.db.models import Article, Comment
from app.db.session import get_session_factory


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2000)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    content: str
    created_at: datetime


router = APIRouter(prefix="/articles", tags=["comments"])


def comment_user(credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)) -> str:
    return require_user(credentials)


@router.get("/{slug}/comments", response_model=list[CommentResponse])
def list_comments(slug: str) -> list[Comment]:
    with get_session_factory()() as session:
        article = session.scalar(select(Article).where(Article.slug == slug, Article.published.is_(True)))
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="article not found")
        statement = select(Comment).where(Comment.article_id == article.id).order_by(Comment.created_at.asc())
        return list(session.scalars(statement))


@router.post("/{slug}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    slug: str,
    comment_input: CommentCreate,
    username: str = Depends(comment_user),
) -> Comment:
    with get_session_factory()() as session:
        article = session.scalar(select(Article).where(Article.slug == slug, Article.published.is_(True)))
        if article is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="article not found")
        comment = Comment(
            article_id=article.id,
            username=username,
            content=comment_input.content.strip(),
            created_at=datetime.now(UTC),
        )
        if not comment.content:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="comment cannot be empty")
        session.add(comment)
        session.commit()
        session.refresh(comment)
        return comment

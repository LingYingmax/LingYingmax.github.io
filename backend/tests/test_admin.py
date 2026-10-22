from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_engine
from app.main import app


@pytest.fixture
def client(monkeypatch) -> Iterator[TestClient]:
    database_path = Path(__file__).with_name("admin-test.db")
    database_path.unlink(missing_ok=True)
    monkeypatch.setattr(settings, "database_url", f"sqlite:///{database_path.as_posix()}")
    get_engine.cache_clear()
    Base.metadata.create_all(get_engine())
    yield TestClient(app)
    get_engine().dispose()
    get_engine.cache_clear()
    database_path.unlink(missing_ok=True)


def test_admin_can_login_and_manage_articles(client: TestClient) -> None:
    unauthorized = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert unauthorized.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "change-me"},
    )
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    created = client.post(
        "/api/admin/articles",
        headers=headers,
        json={
            "slug": "admin-test",
            "title": "Admin test",
            "summary": "A test article",
            "content": "Content",
            "published": True,
            "published_on": "2026-10-20",
        },
    )
    assert created.status_code == 201
    article_id = created.json()["id"]

    updated = client.put(
        f"/api/admin/articles/{article_id}",
        headers=headers,
        json={"title": "Updated title"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated title"

    user_login = client.post(
        "/api/auth/login",
        json={"username": "user", "password": "change-me-user"},
    )
    user_headers = {"Authorization": f"Bearer {user_login.json()['access_token']}"}
    comment = client.post(
        "/api/articles/admin-test/comments",
        headers=user_headers,
        json={"content": "A user comment"},
    )
    assert comment.status_code == 201
    assert client.get("/api/articles/admin-test/comments").json()[0]["content"] == "A user comment"

    deleted = client.delete(f"/api/admin/articles/{article_id}", headers=headers)
    assert deleted.status_code == 204
    assert client.get("/api/articles/admin-test").status_code == 404

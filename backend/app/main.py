from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.articles import router as articles_router
from app.api.admin import router as admin_router
from app.api.auth import router as auth_router
from app.api.comments import router as comments_router
from app.api.health import router as health_router


app = FastAPI(title="LingYingmax Blog API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
app.include_router(health_router, prefix="/api")
app.include_router(articles_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(comments_router, prefix="/api")

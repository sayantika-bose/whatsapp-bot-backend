from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models.article_model import ArticleResponse, ArticleCreate, ArticleUpdate
from models.database import get_db
from services import article_service

router = APIRouter()


@router.post("/", response_model=ArticleResponse)
def create_article(article: ArticleCreate, db: Session = Depends(get_db)):
    return article_service.create_article(db, article)


@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(article_id: int, db: Session = Depends(get_db)):
    article = article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.get("/", response_model=List[ArticleResponse])
def list_articles(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return article_service.get_all_articles(db, skip, limit)


@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(article_id: int, update_data: ArticleUpdate, db: Session = Depends(get_db)):
    article = article_service.update_article(db, article_id, update_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article


@router.delete("/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    article = article_service.delete_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"detail": "Article deleted successfully"}
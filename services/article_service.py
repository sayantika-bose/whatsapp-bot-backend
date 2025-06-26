from sqlalchemy.orm import Session

from models.article_model import ArticleUpdate, ArticleCreate
from models.database import Article


def create_article(db: Session, article_data: ArticleCreate):
    article = Article(
        advisor_id=article_data.advisor_id,
        title=article_data.title,
        content=article_data.content,
        image_base64=article_data.image_base64,
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


def get_article(db: Session, article_id: int):
    return db.query(Article).filter(Article.id == article_id).first()


def get_all_articles(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Article).offset(skip).limit(limit).all()


def update_article(db: Session, article_id: int, update_data: ArticleUpdate):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        if update_data.title is not None:
            article.title = update_data.title
        if update_data.content is not None:
            article.content = update_data.content
        db.commit()
        db.refresh(article)
    return article


def delete_article(db: Session, article_id: int):
    article = db.query(Article).filter(Article.id == article_id).first()
    if article:
        db.delete(article)
        db.commit()
    return article
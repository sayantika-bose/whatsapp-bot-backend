import logging
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
load_dotenv()

Base = declarative_base()

# [Model definitions remain the same as before...]
class DecisionTreeQuestion(Base):
    __tablename__ = "decision_tree_questions"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    advisor_id = Column(Integer, ForeignKey("financial_advisors.id"))
    question = Column(String(10000), nullable=False)
    triggerKeyword = Column(String(50))
    step = Column(Integer, nullable=False)
    next_step = Column(Integer)
    is_predefined_answer = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    salutation = Column(String(10))
    name = Column(String(100), nullable=False)
    mobile_number = Column(String(20), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    advisor_id = Column(Integer, ForeignKey("financial_advisors.id"))
    age_group = Column(String(20))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class FinancialAdvisor(Base):
    __tablename__ = "financial_advisors"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    mobile_number = Column(String(20), unique=True)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)

class UserReply(Base):
    __tablename__ = "user_replies"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("decision_tree_questions.id"))
    reply = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    try:
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

def get_db():
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        db.close()
import logging
from sqlalchemy.types import Enum as SqlEnum
from sqlalchemy import Column, Float, Integer, String, Boolean, ForeignKey, Text, create_engine, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Mapped, mapped_column
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

from models.enums import AnswerLabel

logger = logging.getLogger(__name__)
load_dotenv()

Base = declarative_base()

class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_token = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    answers = relationship("UserAnswer", back_populates="session")

class UserInvestorProfile(Base):
    __tablename__ = "user_investor_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    profile_id = Column(Integer, ForeignKey("investor_profiles.id"))
    percentage = Column(Float)
    created_at = Column(DateTime, default=datetime.now)

    profile = relationship("InvestorProfile", back_populates="user_profiles")

class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(Text, nullable=False)
    is_scored = Column(Boolean, default=True)

    answers = relationship("QuizAnswer", back_populates="question")

class InvestorProfile(Base):
    __tablename__ = "investor_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    emoji = Column(String(10))
    ponderation: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    
    answers = relationship("QuizAnswer", back_populates="profile")
    user_profiles = relationship("UserInvestorProfile", back_populates="profile")

class QuizAnswer(Base):
    __tablename__ = "quiz_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    label = Column(SqlEnum(AnswerLabel, name="answer_label_enum", values_callable=lambda x: [e.value for e in x]), nullable=False)
    text = Column(Text, nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    profile_id = Column(Integer, ForeignKey("investor_profiles.id"), nullable=False)

    question = relationship("QuizQuestion", back_populates="answers")
    profile = relationship("InvestorProfile", back_populates="answers")
    user_answers = relationship("UserAnswer", back_populates="answer")

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    answered_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    answer_id = Column(Integer, ForeignKey("quiz_answers.id"), nullable=False)

    session = relationship("QuizSession", back_populates="answers")
    answer = relationship("QuizAnswer", back_populates="user_answers")
    question = relationship("QuizQuestion")

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
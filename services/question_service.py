import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import DecisionTreeQuestion

logger = logging.getLogger(__name__)

def add_question(db: Session, advisor_id: int, question: str, triggerKeyword: str, is_predefined_answer: bool):
    logger.info(f"Adding question for advisor_id: {advisor_id}")
    max_step = db.query(func.max(DecisionTreeQuestion.step)).filter_by(advisor_id=advisor_id).scalar() or 0
    new_question = DecisionTreeQuestion(
        advisor_id=advisor_id,
        question=question,
        triggerKeyword=triggerKeyword,
        step=max_step + 1,
        next_step=max_step + 2,
        is_predefined_answer=is_predefined_answer
    )
    db.add(new_question)
    db.commit()
    logger.info(f"Question added with ID: {new_question.id}")
    return new_question

def get_questions(db: Session, advisor_id: int):
    logger.debug(f"Fetching questions for advisor_id: {advisor_id}")
    questions = db.query(DecisionTreeQuestion).filter_by(advisor_id=advisor_id).all()
    logger.info(f"Retrieved {len(questions)} questions for advisor_id: {advisor_id}")
    return questions

def update_question(db: Session, question_id: int, step: int, question: str):
    logger.info(f"Updating question ID: {question_id}")
    q = db.query(DecisionTreeQuestion).filter_by(id=question_id).first()
    if q:
        q.step = step
        q.question = question
        db.commit()
        logger.info(f"Question ID: {question_id} updated successfully")
        return True
    logger.warning(f"Question ID: {question_id} not found")
    return False

def delete_question(db: Session, question_id: int):
    logger.info(f"Deleting question ID: {question_id}")
    question = db.query(DecisionTreeQuestion).filter_by(id=question_id).first()
    if question:
        db.delete(question)
        db.commit()
        remaining_questions = db.query(DecisionTreeQuestion).order_by(DecisionTreeQuestion.id).all()
        for idx, q in enumerate(remaining_questions, 1):
            q.id = idx
        db.commit()
        logger.info(f"Question ID: {question_id} deleted and IDs reordered")
        return True
    logger.warning(f"Question ID: {question_id} not found for deletion")
    return False
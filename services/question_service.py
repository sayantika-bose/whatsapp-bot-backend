import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.database import DecisionTreeQuestion
from utils.html_converter import html_to_whatsapp_format 

logger = logging.getLogger(__name__)

def add_question(db: Session, advisor_id: int, question: str, triggerKeyword: str, is_predefined_answer: bool):
    logger.info(f"Adding question for advisor_id: {advisor_id}")

    whatsapp_question = html_to_whatsapp_format(question)

    max_step = db.query(func.max(DecisionTreeQuestion.step)).filter_by(advisor_id=advisor_id).scalar() or 0
    new_question = DecisionTreeQuestion(
        advisor_id=advisor_id,
        question=whatsapp_question,
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
    whatsapp_question = html_to_whatsapp_format(question)
    if q:
        q.step = step
        q.question = whatsapp_question
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

        # Fetch all remaining questions ordered by step (not id)
        remaining_questions = db.query(DecisionTreeQuestion).filter_by(
            advisor_id=question.advisor_id
        ).order_by(DecisionTreeQuestion.step).all()

        # Reassign step and next_step properly
        for index, q in enumerate(remaining_questions, start=1):
            q.step = index
            q.next_step = index + 1

        db.commit()
        logger.info(f"Question ID: {question_id} deleted and steps/next_steps updated")
        return True

    logger.warning(f"Question ID: {question_id} not found for deletion")
    return False

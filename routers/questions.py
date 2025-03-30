import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.question_service import add_question, get_questions, update_question, delete_question
from models.database import get_db
from models.questions_model import AddQuestionRequest, UpdateQuestionRequest, QuestionListResponse, QuestionResponse, MessageResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/add", response_model=MessageResponse)
def add_question_route(data: AddQuestionRequest, db: Session = Depends(get_db)):
    try:
        logger.info("Add question request received")
        add_question(
            db, 
            data.advisor_id, 
            data.question, 
            data.triggerKeyword, 
            data.is_predefined_answer
        )
        return {"message": "Question added successfully"}
    except Exception as e:
        logger.error(f"Error adding question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{advisor_id}", response_model=QuestionListResponse)
def get_questions_route(advisor_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Get questions request for advisor_id: {advisor_id}")
        questions = get_questions(db, advisor_id)
        return {"questions": [
            QuestionResponse(id=q.id, step=q.step, question=q.question, triggerKeyword=q.triggerKeyword) 
            for q in questions
        ]}
    except Exception as e:
        logger.error(f"Error retrieving questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{id}", response_model=MessageResponse)
def update_question_route(id: int, data: UpdateQuestionRequest, db: Session = Depends(get_db)):
    try:
        logger.info(f"Update question request for ID: {id}")
        if update_question(db, id, data.step, data.question):
            return {"message": "Question updated successfully"}
        raise HTTPException(status_code=404, detail="Question not found")
    except Exception as e:
        logger.error(f"Error updating question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{id}", response_model=MessageResponse)
def delete_question_route(id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Delete question request for ID: {id}")
        if delete_question(db, id):
            return {"message": "Question deleted and IDs reordered successfully"}
        raise HTTPException(status_code=404, detail="Question not found")
    except Exception as e:
        logger.error(f"Error deleting question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

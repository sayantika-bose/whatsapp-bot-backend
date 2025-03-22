import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services.question_service import add_question, get_questions, update_question, delete_question
from models.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/add")
def add_question_route(data: dict, db: Session = Depends(get_db)):
    try:
        logger.info("Add question request received")
        question = add_question(
            db, 
            data["advisor_id"], 
            data["question"], 
            data["triggerKeyword"], 
            data.get("is_predefined_answer", False)
        )
        return {"message": "Question added successfully"}
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        logger.error(f"Error adding question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{advisor_id}")
def get_questions_route(advisor_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Get questions request for advisor_id: {advisor_id}")
        questions = get_questions(db, advisor_id)
        return [{"id": q.id, "step": q.step, "question": q.question, "triggerKeyword": q.triggerKeyword} 
                for q in questions]
    except Exception as e:
        logger.error(f"Error retrieving questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{id}")
def update_question_route(id: int, data: dict, db: Session = Depends(get_db)):
    try:
        logger.info(f"Update question request for ID: {id}")
        if update_question(db, id, data["step"], data["question"]):
            return {"message": "Question updated successfully"}
        raise HTTPException(status_code=404, detail="Question not found")
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        logger.error(f"Error updating question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{id}")
def delete_question_route(id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f"Delete question request for ID: {id}")
        if delete_question(db, id):
            return {"message": "Question deleted and IDs reordered successfully"}
        raise HTTPException(status_code=404, detail="Question not found")
    except Exception as e:
        logger.error(f"Error deleting question: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
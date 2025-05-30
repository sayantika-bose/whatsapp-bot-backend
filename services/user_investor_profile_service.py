from sqlalchemy.orm import Session
from models.database import InvestorProfile, UserAnswer, QuizAnswer, UserInvestorProfile
from collections import defaultdict

from models.user_investor_profile_model import UserInvestorProfileResponse

def calculate_and_save_user_profile(db: Session, user_id: int) -> list[UserInvestorProfileResponse]:
    db.query(UserInvestorProfile).filter_by(user_id=user_id).delete()
    db.commit()

    answers = db.query(UserAnswer).filter_by(user_id=user_id).all()

    profile_scores = defaultdict(float)

    for answer in answers:
        quiz_answer = db.query(QuizAnswer).filter_by(id=answer.answer_id).first()
        if quiz_answer and quiz_answer.profile_id:
            profile = db.query(InvestorProfile).filter_by(id=quiz_answer.profile_id).first()
            if profile:
                ponderation = float(profile.ponderation) if profile.ponderation is not None else 1.0
                profile_scores[quiz_answer.profile_id] += ponderation

    total_score = sum(profile_scores.values())
    results = []

    if total_score == 0:
        return results  

    for profile_id, score in profile_scores.items():
        percentage = round((score / total_score) * 100, 1)  
        new_profile = UserInvestorProfile(
            user_id=user_id,
            profile_id=profile_id,
            percentage=percentage,
        )
        db.add(new_profile)
        db.flush()
        db.refresh(new_profile)
        results.append(new_profile)

    db.commit()
    return results

def get_user_investor_profiles(db: Session, user_id: int) -> list[UserInvestorProfile]:
    profiles = (
        db.query(UserInvestorProfile)
        .filter_by(user_id=user_id)
        .order_by(UserInvestorProfile.percentage.desc())
        .all()
    )
    return profiles
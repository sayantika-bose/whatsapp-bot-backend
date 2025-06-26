import re
import unicodedata

from sqlalchemy.orm import Session
from fastapi import HTTPException
from models.database import InvestorProfile
from models.investor_profile_model import InvestorProfileCreate, InvestorProfileUpdate, InvestorProfileResponse

def generate_slug(text: str) -> str:
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')
    return text

def create_profile(db: Session, profile_data: InvestorProfileCreate) -> InvestorProfileResponse:
    existing = db.query(InvestorProfile).filter_by(name=profile_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Investor profile with this name already exists")

    slug = generate_slug(profile_data.name)
    slug_exists = db.query(InvestorProfile).filter_by(slug=slug).first()
    if slug_exists:
        raise HTTPException(status_code=400, detail="Slug already exists. Please choose a different name.")

    profile = InvestorProfile(**profile_data.model_dump(), slug=slug)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return InvestorProfileResponse.model_validate(profile)

def get_all_profiles(db: Session):
    return db.query(InvestorProfile).all()

def get_profile_by_id(db: Session, profile_id: int) -> type[InvestorProfile]:
    profile = db.query(InvestorProfile).filter_by(id=profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Investor profile not found")
    return profile

def update_profile(db: Session, profile_id: int, update_data: InvestorProfileUpdate) -> InvestorProfileResponse:
    profile = get_profile_by_id(db, profile_id)

    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return InvestorProfileResponse.model_validate(profile)

def delete_profile(db: Session, profile_id: int):
    profile = get_profile_by_id(db, profile_id)
    db.delete(profile)
    db.commit()
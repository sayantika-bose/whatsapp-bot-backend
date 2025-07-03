from utils.encryption import decrypt_string
from models.database import User
from models.user_model import UserResponse

def user_to_response(user: User, is_admin: bool) -> UserResponse:
    try:
        return UserResponse(
            id=user.id,
            gender=GenderEnum(decrypt_string(user.gender)) if is_admin and user.gender else GenderEnum.UNSPECIFIED,
            name=f"{decrypt_string(user.first_name)} {decrypt_string(user.last_name)}" if is_admin else "**** ****",
            mobile_number=decrypt_string(user.mobile_number) if is_admin else "****",
            email=decrypt_string(user.email) if is_admin else "****",
            advisor_id=user.advisor_id,
            age_group=AgeGroupEnum(user.age_group) if user.age_group else None,
            created_at=user.created_at,
            success=None,
            message_sid=None,
            message=None,
            timestamp=datetime.now()
        )
    except Exception as e:
        # This scenario is when the decryption token is wrong for example
        return UserResponse(
            id=user.id,
            gender=GenderEnum.UNSPECIFIED,
            name="**** ****",
            mobile_number="****",
            email="****",
            advisor_id=user.advisor_id,
            age_group=None,
            created_at=user.created_at,
            success=False,
            message_sid=None,
            message="Erreur de lecture des données",
            timestamp=datetime.now()
        )
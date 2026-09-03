from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.user import UserResponse
from app.models.user import User
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_users(db: Session = Depends(get_db)):
    """
    Retrieve all users.
    """
    users_db = db.query(User).all()
    # Format time nicely for demo
    return [
        UserResponse(
            id=u.id,
            name=u.name,
            email=u.email,
            role=u.role,
            status=u.status,
            lastActive="2 mins ago" # Normally formatted delta
        ) for u in users_db
    ]

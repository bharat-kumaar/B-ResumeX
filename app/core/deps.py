from fastapi import Depends, HTTPException, status, Request
from sqlmodel import Session
from app.core.db import get_session
from app.core.security import SECRET_KEY, ALGORITHM
from app.models.domain import User
import jwt

def get_current_user_optional(request: Request, session: Session = Depends(get_session)) -> User | None:
    token = request.cookies.get("resumate_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            return None
        user = session.get(User, user_id)
        return user
    except jwt.PyJWTError:
        return None

def get_current_user(user: User | None = Depends(get_current_user_optional)) -> User:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return user

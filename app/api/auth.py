from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session
from app.core.db import get_session
from app.models.domain import User
from app.core.security import get_password_hash, verify_password, create_access_token
from pydantic import BaseModel, EmailStr

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

@router.post("/signup")
async def signup(user_in: UserCreate, response: Response, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_in.password)
    db_user = User(email=user_in.email, name=user_in.name, password_hash=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    access_token = create_access_token(data={"sub": db_user.id})
    response.set_cookie(key="resumate_token", value=access_token, httponly=True, max_age=60*60*24*7)
    return {"success": True}

@router.post("/login")
async def login(user_in: UserLogin, response: Response, session: Session = Depends(get_session)):
    user = session.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token = create_access_token(data={"sub": user.id})
    response.set_cookie(key="resumate_token", value=access_token, httponly=True, max_age=60*60*24*7)
    return {"success": True}

@router.post("/logout")
@router.get("/logout")
async def logout(response: Response):
    from fastapi.responses import RedirectResponse
    res = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    res.delete_cookie(key="resumate_token", path="/")
    return res

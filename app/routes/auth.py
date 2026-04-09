from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserRegister, UserLogin, TokenOut, UserOut
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name          = payload.name,
        email         = payload.email,
        password_hash = hash_password(payload.password),
        role          = payload.role,
        status        = UserStatus.active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


from fastapi.security import OAuth2PasswordRequestForm

@router.post("/login", response_model=TokenOut)
def login(payload: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if user.status.value == "inactive":
        raise HTTPException(status_code=403, detail="Account inactive. Contact admin.")
    token = create_access_token({"id": user.id, "sub": user.email, "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
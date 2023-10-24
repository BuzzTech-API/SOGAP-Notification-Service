from fastapi import APIRouter, Depends, HTTPException, status
from database import schemas
from sqlalchemy.orm import Session
from models import oauth2, user_crud, JWTtoken
from database.database import get_db
from typing import Annotated, List
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from passlib.context import CryptContext
from .twofactor import verify_2fa
import pyotp #Importando a biblioteca PyOTP para autenticação em 2 fatores

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

## Verifica a senha
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

ACCESS_TOKEN_EXPIRE_MINUTES = 30

router = APIRouter(tags=["Login"])


@router.post("/login")
async def login(login: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    print(pwd_context.hash('adm'))
    user = user_crud.get_user_by_email(email=login.username, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )
    if not verify_password(login.password,user.password):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Invalid Credentials"
        )
    
    # Aqui é a verificação 2FA
    if user.is_2fa_enable:
        login_token = JWTtoken.create_login_token(
        data={'sub': user.email}
        )
        return {"login_token": login_token,"is_enabled2fa": True}
          
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = JWTtoken.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = JWTtoken.create_refresh_token(
        data={"sub": user.email}
    )

    return {"access_token": access_token, "refresh_token":refresh_token, "token_type": "bearer"}

@router.get("/refresh_token")
async def refresh_user(
    current_user: Annotated[dict, Depends(oauth2.refresh_user_token)],
):
    return current_user
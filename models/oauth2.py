from fastapi import Depends, HTTPException, Request, WebSocket, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Annotated
from models import JWTtoken
from jose import JWTError, jwt
from database.database import get_db
from database import schemas
from models import user_crud
from database.schemas import TokenData
from sqlalchemy.orm import Session



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



async def get_current_user_login(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    """Pega o usuario atual"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return JWTtoken.verify_login_token(
        token=token, credentials_exception=credentials_exception, db=db
    )

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    """Pega o usuario atual"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return JWTtoken.verify_token(
        token=token, credentials_exception=credentials_exception, db=db
    )

async def refresh_user_token(
    token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)
):
    """Pega o usuario atual"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return JWTtoken.refresh_token(
        token=token, credentials_exception=credentials_exception, db=db
    )

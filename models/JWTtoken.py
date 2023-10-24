from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
from typing import Annotated, Any, Union
from models import user_crud, JWTtoken
from pydantic import BaseModel
from database.schemas import TokenData
import os
from dotenv import dotenv_values

# Python Environment Variable setup required on System or .env file
config_env = {
    **dotenv_values(".env"),  # load local file development variables
    **os.environ,  # override loaded values with system environment variables
}



ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 2 # 2 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = config_env['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = config_env['JWT_REFRESH_SECRET_KEY']   # should be kept secret
JWT_LOGIN_SECRET_KEY = config_env['JWT_LOGIN_SECRET_KEY']


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """Realiza a criação do token de autenticação"""
    
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class TokenData(BaseModel):
    username: Optional[str] = None

# Função para verificar o token JWT
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="login"))):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenData(**payload)
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    return token_data




def verify_token(token: str, credentials_exception, db):
    """Verifica se aquele token é verdadeiro"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
        if email is None:
            raise credentials_exception
        if datetime.fromtimestamp(payload.get('exp')) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise credentials_exception
    user = user_crud.get_user_by_email(db=db, email=email)
    if user is None:
        raise credentials_exception
    return user

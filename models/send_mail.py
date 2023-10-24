from typing import List

from fastapi import BackgroundTasks, FastAPI
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from starlette.responses import JSONResponse

from dotenv import dotenv_values

#credenciais
credentials = dotenv_values("./.env")


class EmailSchema(BaseModel):
    email: List[EmailStr]

content = {"Email enviado com sucesso!"}

conf = ConnectionConfig(
    MAIL_USERNAME = credentials['EMAIL'],
    MAIL_PASSWORD = 'apzh jhqd pzrk jivt', #Senha de app dentro de Segurança/Verificação em duas etapas
    MAIL_FROM = credentials['EMAIL'],
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

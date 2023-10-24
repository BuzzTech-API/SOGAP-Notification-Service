from datetime import timedelta
from fastapi import APIRouter, HTTPException, status, Depends
from models import user_crud, oauth2, JWTtoken
from database.database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from database import schemas
import pyotp, qrcode
import hashlib
import base64
import os
from dotenv import dotenv_values

router = APIRouter()

config_env = {
    **dotenv_values(".env"),  # load local file development variables
    **os.environ,  # override loaded values with system environment variables
}
OTP_KEY = config_env["OTP_KEY"]  # should be kept secret


def generate_base32_key(input_string):
    # Use o SHA-256 como algoritmo de hash (você pode escolher outro, se preferir)
    sha256_hash = hashlib.sha256(input_string.encode())

    # Obtenha o valor hexadecimal do hash
    hex_hash = sha256_hash.hexdigest()

    # Converta o valor hexadecimal para base32
    base32_key = base64.b32encode(bytes.fromhex(hex_hash)).decode()

    # Garanta que a chave tenha 32 caracteres (caso contrário, ajuste conforme necessário)
    if len(base32_key) < 32:
        base32_key = base32_key.ljust(32, "=")
    return base32_key


# Rota para habilitar o 2FA
@router.post("/enable-2fa")
def enable_2fa(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    # Aqui geramos uma chave secreta para o usuário em formato QR code base32
    user = current_user
    
    secret_key = OTP_KEY + user.email

    user_crud.save_secret_key(id=user.id, db=db, secret_key=secret_key)
    # Aqui criamos uma URI para o código QR
    uri = pyotp.totp.TOTP(generate_base32_key(secret_key)).provisioning_uri(
        name=user.name,
        issuer_name="SOGAP | IonicHealth",
    )
    # Aqui geramos a imagem do QR code e armazenamos em uma variavel chamada img

    # No retorno da função iremos retornar a chave secreta e a img
    return {"secret_key": secret_key, "qr_code_image": uri}


# Rota para verificar o código 2FA
@router.post("/verify-2fa")
def verify_2fa(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user_login)],
    verification_code: schemas.VerificationCode,
    db: Session = Depends(get_db),
):
    secret_key = OTP_KEY + current_user.email
    if secret_key:
        totp = pyotp.TOTP(generate_base32_key(secret_key))

        if totp.verify(verification_code.verification_code) == True:
            print("Entrei no Verify")
            access_token_expires = timedelta(minutes=30)
            access_token = JWTtoken.create_access_token(
                data={"sub": current_user.email}, expires_delta=access_token_expires
            )
            refresh_token = JWTtoken.create_refresh_token(
                data={"sub": current_user.email}
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }

        else:
            # O código 2FA é inválido, então retorne uma exceção HTTP
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código 2FA inválido. Acesso negado.",
            )


@router.post("/verify-2fa-First-Auth")
def verify_2fa_First_Auth(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    verification_code: schemas.VerificationCode,
    db: Session = Depends(get_db),
):
    
    secret_key = OTP_KEY + current_user.email
    if secret_key:
        totp = pyotp.TOTP(generate_base32_key(secret_key))
        if totp.verify(verification_code.verification_code) == True:
            user_crud.enable_2fa_first_auth(db=db, id=current_user.id)
            return {"verify": True}
        else:
            # O código 2FA é inválido, então retorne uma exceção HTTP
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Código 2FA inválido. Acesso negado.",
            )


@router.put("/deactivate2fa")
def deactivate_2fa(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    user_crud.disable_2fa(db=db, id=current_user.id)
    return {'deactivated': True}

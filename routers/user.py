from fastapi import APIRouter, Depends, HTTPException
from database import schemas
from sqlalchemy.orm import Session
from models import user_crud, oauth2
from database.database import get_db, engine
from typing import List, Annotated
from passlib.context import CryptContext

router = APIRouter(tags=["Users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

## Rotas que trabalham o usuario
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_admin():
    with Session(engine) as session:
        db_user = user_crud.get_user_by_email(session, email="adm@adm")
        if not db_user:
            db_user = user_crud.User(
                email="adm@adm",
                name="administrador",
                password=pwd_context.hash('adm'),
                role="Administrador",
                team="Administrador",
                is_active=True,
            )
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            session.close()



@router.get("/users/{id}", response_model=schemas.UserGet)
async def get_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    id: int,
    db: Session = Depends(get_db),
):
    """Você coloca o id do usuario e te retorna um json contendo todos seus dados e processos e etapas
    que ele está responsável e caso ele não exista lança um exceção http falando que ele não existe
    """
    user = user_crud.get_user(id=id, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="Não há Usuarios cadastrado")

    return user

@router.get("/user/getall_related_data/")
async def get_related(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    """Você coloca o id do usuario e te retorna um json contendo todos seus dados e processos e etapas
    que ele está responsável e caso ele não exista lança um exceção http falando que ele não existe
    """

    return user_crud.get_user_related_data(db=db, user_id=current_user.id)


@router.get("/users", response_model=List[schemas.User])
async def get_all_users(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    """Você coloca o id do usuario e te retorna um json contendo todos seus dados e processos e etapas
    que ele está responsável e caso ele não exista lança um exceção http falando que ele não existe
    """
    user = user_crud.get_all_user(db=db)

    if not user:
        raise HTTPException(status_code=404, detail="Usuario não existe")

    return user


@router.get("/users/get/me", response_model=schemas.User)
async def read_users_me(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)]
):
    return current_user


@router.post("/users/", response_model=schemas.User)
async def create_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    """Você posta no body os dados do usuario seguindo o modelo da classe UserCreate e se aquele email
    não tiver sido registrado ainda será adicionado o usuario o banco, caso ele exista lança uma http
    exception falando que aquele email ja está registrado"""
    db_user = user_crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    user.password=pwd_context.hash(user.password)
    return user_crud.create_user(db=db, user=user)


@router.put("/users/", response_model=schemas.User)
async def update_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user: schemas.User,
    db: Session = Depends(get_db),
):
    """Você recebe o usuario que você quer alterar e o altera caso ele exista no banco, caso ele não
    exista lança uma exceção dizendo que usuario não foi encontrado"""
    user = user_crud.update_user(user=user, db=db)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario não encotrado")

    return user


@router.delete("/users/{id}")
async def delete_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    id: int,
    db: Session = Depends(get_db),
):
    """Recebe o id do usuario e tenta deletar ele no banco caso ele exista ira deleta-lo e retorna ele
    mostrando seus dados, caso não tenho retornara None"""
    return user_crud.delete_user(id=id, db=db)

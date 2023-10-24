from fastapi import APIRouter, Depends, HTTPException
from database import schemas
from sqlalchemy.orm import Session
from models import process_user_crud, oauth2
from database.database import get_db
from typing import Optional, Annotated

router = APIRouter(tags=["Processes_Users"])


## Processo Usuario rotas


@router.get(
    "/users_processes/{user_id:int}/{process_id:int}",
    response_model=Optional[schemas.ProcessUser],
)
async def get_process_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user_id:int,
    process_id:int,
    db: Session = Depends(get_db),
):
    """Rota para buscar uma relação Usuario-Processo"""
    process_user = process_user_crud.get_process_user_by_user_and_process_id(
        user_id=user_id, process_id=process_id, db=db
    )
    if not process_user:
        raise HTTPException(
            status_code=404, detail="Relação de Processo e usuário não encontrada "
        )
    return process_user


@router.get(
    "/users_processes",
    response_model=Optional[list[schemas.ProcessUser]],
)
async def get_all_process_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    """Rota para buscar todas as relação Usuario-Processo"""
    process_user = process_user_crud.get_process_user_by_process_id_all(
        db=db
    )
    if not process_user:
        raise HTTPException(
            status_code=404, detail="Relação de Processo e usuário não encontrada "
        )
    return process_user

@router.get(
    "/users_processes/user_id/{user_id:int}",
    response_model=Optional[list[schemas.ProcessUser]],
)
async def get_all_process_user_by_user_id(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user_id: int,
    db: Session = Depends(get_db),
):
    """Rota para buscar todas as relação Usuario-Processo"""
    process_user = process_user_crud.get_process_user_by_user_id_all(
        user_id=user_id,
        db=db
    )
    if not process_user:
        raise HTTPException(
            status_code=404, detail="Relação de Processo e usuário não encontrada "
        )
    return process_user

@router.get(
    "/users_processes/process_id/{process_id:int}",
    response_model=Optional[list[schemas.ProcessUser]],
)
async def get_all_process_user_by_process_id(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    process_id: int,
    db: Session = Depends(get_db),
):
    """Rota para buscar todas as relação Usuario-Processo"""
    process_user = process_user_crud.get_process_user_by_process_id_all(
        process_id=process_id,
        db=db
    )
    if not process_user:
        raise HTTPException(
            status_code=404, detail="Relação de Processo e usuário não encontrada "
        )
    return process_user


@router.post("/users_processes/", response_model=Optional[schemas.ProcessUserCreate])
async def create_process_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    process_user: schemas.ProcessUserCreate,
    db: Session = Depends(get_db),
):
    """Rota para criar uma relação Usuario-Processo"""
    return process_user_crud.create_process_user(db=db, process_user=process_user)


@router.delete("/users_processes/", response_model=Optional[schemas.ProcessUserBase])
def delete_process_user(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    process_user: schemas.ProcessUserBase,
    db: Session = Depends(get_db),
):
    """Rota para deletar uma relação Usuario-Processo"""
    print(process_user)
    return process_user_crud.delete_process_user(db=db, user_id=process_user.user_id, process_id=process_user.process_id)

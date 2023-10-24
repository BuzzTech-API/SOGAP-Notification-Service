from fastapi import APIRouter, Depends, HTTPException
from database import schemas
from sqlalchemy.orm import Session
from models import user_step_crud, oauth2
from database.database import get_db
from typing import Annotated, Optional

router = APIRouter(tags=["User_Steps"])


## Usuario Etapas rotas


@router.get("/stepes_users/{user_id}/{step_id}", response_model=Optional[schemas.UserStep])
async def get_user_step(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user_id:int,
    step_id:int,
    db: Session = Depends(get_db),
):
    """Rota para buscar uma relação etapa-usuario"""
    return user_step_crud.get_user_step_by_user_and_step_id(
        user_id=user_id, step_id=step_id, db=db
    )

@router.get("/stepes_users", response_model=Optional[list[schemas.UserStep]])
async def get_all_user_step(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    """Rota para buscar todas relação etapa-usuario"""
    return user_step_crud.get_all_user_step(
        db=db
    )

@router.get("/stepes_users/user_id/{user_id}", response_model=Optional[list[schemas.UserStep]])
async def get_all_user_step_by_user_id(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user_id: int,
    db: Session = Depends(get_db),
):
    """Rota para buscar todas relação etapa-usuario pelo id do usuario"""
    return user_step_crud.get_user_step_by_user_id_all(
        user_id=user_id,
        db=db
    )

@router.get("/stepes_users/step_id/{step_id}", response_model=list[schemas.UserStep])
async def get_all_user_step_by_step_id(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    step_id: int,
    db: Session = Depends(get_db),
):
    """Rota para buscar todas relação etapa-usuario pelo id do usuario"""
    return user_step_crud.get_user_step_by_step_id_all(
        step_id=step_id,
        db=db
    )



@router.post("/stepes_users/", response_model=Optional[schemas.UserStep])
async def create_user_step(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    user_step: schemas.UserStepCreate,
    db: Session = Depends(get_db),
):
    """Rota para criar uma relação etapa-usuario"""
    return user_step_crud.create_user_step(db=db, user_step=user_step)


@router.delete("/stepes_users/")
async def delete_user_step(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    step_user: schemas.UserStepCreate,
    db: Session = Depends(get_db),
):
    """Rota para deletar uma relação etapa-usuario"""
    return user_step_crud.delete_user_step(
        step_id=step_user.step_id, user_id=step_user.user_id, db=db
    )

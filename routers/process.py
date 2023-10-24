from fastapi import APIRouter, Depends, HTTPException
from database import schemas
from sqlalchemy.orm import Session
from models import process_crud, oauth2
from database.database import get_db
from typing import Annotated, Optional

router = APIRouter(tags=["Processes"])


## Processos rotas


@router.get("/processes/{id}", response_model=Optional[schemas.ProcessAll])
async def get_process(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    id: int,
    db: Session = Depends(get_db),
):
    """Rota para buscar processo pelo id"""
    return process_crud.get_process(id=id, db=db)


@router.get("/processes", response_model=Optional[list[schemas.ProcessAll]])
async def get_process_all(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    db: Session = Depends(get_db),
):
    """Rota para buscar processo pelo id"""
    return process_crud.get_all_process(db=db)


@router.post("/processes/", response_model=Optional[schemas.Process])
async def create_process(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    process: schemas.ProcessCreate,
    db: Session = Depends(get_db),
):
    """Rota para criar um novo processo"""
    return process_crud.create_process(db=db, process=process)


@router.put("/processes/", response_model=Optional[schemas.Process])
async def update_process(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    process: schemas.ProcessUpdate,
    db: Session = Depends(get_db),
):
    """Rota para alterar processo pelo id"""
    return process_crud.update_process(process=process, db=db)

@router.put("/processes/delete", response_model=Optional[schemas.DeleteProcess])
async def delete_process(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    deleteProcess: schemas.DeleteProcess,
    db: Session = Depends(get_db),
):
    """Rota para fazer o delete lógico"""
    return process_crud.delete_process(db=db, id=deleteProcess.id, is_active=deleteProcess.is_active)

@router.delete("/processes/{id}")
async def delete_process(
    current_user: Annotated[schemas.User, Depends(oauth2.get_current_user)],
    id: int,
    db: Session = Depends(get_db),
):
    """Rota para deletar processo pelo id"""
    return process_crud.delete_process(id=id, db=db)

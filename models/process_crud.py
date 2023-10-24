from typing import List
from sqlalchemy.orm import Session
from database import schemas
from database.database import Base
from sqlalchemy import Boolean, Column, Integer, String, Date
from sqlalchemy.orm import relationship, Mapped
from models import request_for_evidence_crud
from models.step_crud import Step
from models.process_user_crud import ProcessUser



class Process(Base):
    """Classe que trabalha a tabela de processos no banco
    com atributos que mostra todas as etapas cadastrado no prcesso
    atributo que mostra todas as suas relação Processo-Usuario
    """

    __tablename__ = "process"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(60))
    description = Column(String(300))
    objective = Column(String(200))
    endingDate = Column(Date)
    createDate = Column(Date)
    lastUpdate = Column(Date)
    is_active = Column(Boolean, default=True)
    priority = Column(String(60))
    status = Column(String(60))
    steps = relationship(
        Step,
        primaryjoin="and_(Process.id == Step.process_id, Step.is_active == True)",
        order_by=Step.order,
        viewonly=True,
    )
    users: Mapped[List["ProcessUser"]] = relationship(back_populates="process")


def get_process(db: Session, id: int):
    """Busca o processo no banco pelo o id"""
    return db.query(Process).filter(Process.id == id).first()


def get_all_process(db: Session, skip: int = 0, limit: int = 100):
    """Busca todos os processos no banco limitando a busca a 100 por vez podendo paginar de 100 em 100"""
    return (
        db.query(Process)
        .order_by(Process.id)
        .where(Process.is_active == True)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_process(db: Session, process: schemas.ProcessCreate):
    """Cria um novo processo no banco"""
    db_process = Process(
        title=process.title,
        description=process.description,
        objective=process.objective,
        endingDate=process.endingDate,
        createDate=process.createDate,
        lastUpdate=process.lastUpdate,
        is_active=process.is_active,
        priority=process.priority,
        status=process.status,
    )
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


def update_process(db: Session, process: schemas.Process):
    """Se existir, altera o processo no banco"""
    db_process = db.query(Process).filter(Process.id == process.id).first()

    if db_process:
        db_process.title = process.title
        db_process.description = process.description
        db_process.objective = process.objective
        db_process.endingDate = process.endingDate
        db_process.createDate = process.createDate
        db_process.lastUpdate = process.lastUpdate
        db_process.is_active = process.is_active
        db_process.priority = process.priority
        db_process.status = process.status

        db.commit()
        db.refresh(db_process)

    return db_process


def delete_process(db: Session, id: int, is_active: Boolean):
    """Se existir, deleta o processo no banco pelo o id dele"""
    db_process = db.query(Process).filter(Process.id == id).first()

    if db_process:
        db_process.is_active = is_active

        db.commit()
        db.refresh(db_process)

    return db_process

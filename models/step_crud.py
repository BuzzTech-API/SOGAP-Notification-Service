from sqlalchemy.orm import Session
from database import schemas
from database.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped
from models.request_for_evidence_crud import RequestForEvidence
from models.user_step_crud import UserStep
from typing import List


class Step(Base):
    """Classe para trabalhar a tabela de Etapa, com 2 campos que facilitam as buscas que listam todas requisições de evidencia e os usuario relacionado com a etapa"""

    __tablename__ = "step"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64))
    objective= Column(String(300))
    endingDate= Column(Date)
    endDate = Column(Date)
    process_id = Column(Integer, ForeignKey("process.id"))
    priority = Column(String(20))
    order = Column(Integer)
    is_active = Column(Boolean, default=True)
    requests = relationship(RequestForEvidence, primaryjoin="and_(Step.id == RequestForEvidence.step_id, RequestForEvidence.is_actived == True)", viewonly=True)
    users: Mapped[List["UserStep"]] = relationship(back_populates="step")
    process = relationship("Process")


def get_step(db: Session, id: int):
    """Recebe o id e retorna a etapa do id do banco"""
    return db.query(Step).filter(Step.id == id).first()


def get_all_step(db: Session, skip: int = 0, limit: int = 100):
    """retorn todas as etapas com limit de 100 etapas"""
    return db.query(Step).offset(skip).limit(limit).all()


def create_step(db: Session, step: schemas.StepCreate):
    """Cria uma nova etapa no banco de dados"""
    db_step = Step(
        name=step.name,
        objective= step.objective,
        endingDate= step.endingDate,
        endDate=step.endDate,
        process_id=step.process_id,
        priority=step.priority,
        order=step.order,
        is_active=step.is_active,
    )
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step


def update_step(db: Session, step: schemas.UpdateStep):
    """Se a etapa existir no banco realiza as alterações no banco e salva"""
    db_step = db.query(Step).filter(Step.id == step.step_id).first()

    if db_step:
        db_step.name = step.name
        db_step.objective= step.objective
        db_step.endingDate= step.endingDate
        db_step.endDate = step.endDate
        db_step.process_id = step.process_id
        db_step.priority = step.priority
        db_step.order = step.order
        db_step.is_active = step.is_active

        db.commit()
        db.refresh(db_step)

    return db_step


def delete_step(db: Session, id: int):
    """Se a etapa existir, ela é deleta pelo id dela"""
    db_step = db.query(Step).filter(Step.id == id).first()

    if db_step:
        db.delete(db_step)
        db.commit()

    return db_step

def logical_delete_step(db: Session, id: int):
    """Se a etapa existir, ela é deleta pelo id dela"""
    db_step = db.query(Step).filter(Step.id == id).first()

    if db_step:
        db_step.is_active=False
        db.commit()

    return db_step

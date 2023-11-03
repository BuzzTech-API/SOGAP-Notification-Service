from sqlalchemy.orm import Session
from database import schemas
from database.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship


class Validation(Base):
    """Classe que trabalha a tabela de notificações
    e também contém um campo com as evidencia que estão relacionadas a ela
    """

    __tablename__ = "validation"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    evidence_id = Column(Integer, ForeignKey("evidence.id"))
    reason = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    is_validated = Column(Boolean, default=False)


def get_validation(db: Session, id: int):
    """Busca no banco ao pedido de evidencia pelo id e retorna ela"""
    return db.query(Validation).filter(Validation.id == id).first()


def get_all_validation(db: Session, skip: int = 0, limit: int = 100):
    """Busca no banco todos os pedidos de evidencia, porém limitando a busca a 100 por vez"""
    return db.query(Validation).offset(skip).limit(limit).all()


def create_validation(db: Session, validation: schemas.ValidationCreate):
    """Cria um novo pedido de evidencia no banco"""
    db_validation = Validation(
        evidence_id=validation.evidence_id,
        reason=validation.reason,
        user_id=validation.user_id,
        is_validated=validation.is_validated,
    )
    db.add(db_validation)
    db.commit()
    db.refresh(db_validation)
    return db_validation


def update_validation(db: Session, validation: schemas.Validation):
    """Se o pedido de evidencia existir, altera ele no banco"""
    db_validation = (
        db.query(Validation).filter(Validation.id == Validation.id).first()
    )

    if db_validation:
        db_validation.evidence_id=validation.evidence_id,
        db_validation.reason=validation.reason,
        db_validation.user_id=validation.user_id,
        db_validation.is_validated=validation.is_validated,
        db.commit()
        db.refresh(db_validation)

    return db_validation


def delete_validation(db: Session, id: int):
    """Se o pedido de evidencia existir, deleta ele do banco"""
    db_validation = db.query(Validation).filter(Validation.id == id).first()

    if db_validation:
        db.delete(db_validation)
        db.commit()

    return db_validation
from sqlalchemy.orm import Session
from database import schemas
from database.database import Base
from sqlalchemy import Column,Boolean, ForeignKey, Integer, String, Date


class Evidence(Base):
    """Classe para trabalhar a tabela de evidencia do banco"""

    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    link = Column(String(150))
    idRequestForEvidence = Column(Integer, ForeignKey("request_for_evidence.id"))
    deliveryDate = Column(Date)
    is_active = Column(Boolean, default=True)


def get_evidence(db: Session, id: int):
    """Busca a evidencia pelo id dela e retorna ela"""
    return db.query(Evidence).filter(Evidence.id == id).first()


def get_all_evidence(db: Session, skip: int = 0, limit: int = 100):
    """Retorna todas as evidencia do banco mas somente as 100 primeiras podendo ser paginado outras"""
    return db.query(Evidence).offset(skip).limit(limit).all()


def create_evidence(db: Session, evidence: schemas.EvidenceCreate):
    """Cria uma nova evidencia no banco"""
    db_evidence = Evidence(
        link=evidence.link,
        idRequestForEvidence=evidence.idRequestForEvidence,
        deliveryDate=evidence.deliveryDate,
    )
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence


def update_evidence(db: Session, evidence: schemas.Evidence):
    """Se exister a evidencia no banco realiza a alteração dela e salva as alterações"""
    db_evidence = db.query(Evidence).filter(Evidence.id == evidence.id).first()

    if db_evidence:
        db_evidence.link = evidence.link
        db_evidence.idRequestForEvidence = evidence.idRequestForEvidence
        db_evidence.deliveryDate = evidence.deliveryDate
        db_evidence.is_active = evidence.is_active

        db.commit()
        db.refresh(db_evidence)

    return db_evidence


def delete_evidence(db: Session, id: int):
    """Se a evidencia existir no banco é realizado a exclusão dela no banco pelo id dela"""
    db_evidence = db.query(Evidence).filter(Evidence.id == id).first()

    if db_evidence:
        db.delete(db_evidence)
        db.commit()

    return db_evidence

def invalidate_evidence(db: Session, id: int):
    """Se a evidencia existir no banco é realizado a exclusão dela no banco pelo id dela"""
    db_evidence = db.query(Evidence).filter(Evidence.id == id).first()

    if db_evidence:
        db_evidence.is_active=False
        db.commit()

    return db_evidence

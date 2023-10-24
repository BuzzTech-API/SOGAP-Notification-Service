from sqlalchemy.orm import Session
from database import schemas
from database.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped


class ProcessUser(Base):
    """Class que trabalha a relação Processo-Usuario no banco com
    um campo que mostra usuario da relação e outro o proceso"""

    __tablename__ = "process_user"
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    process_id: Mapped[int] = mapped_column(ForeignKey("process.id"), primary_key=True)
    user: Mapped["User"] = relationship(back_populates="processes")
    process: Mapped["Process"] = relationship(back_populates="users")


def get_process_user_by_user_and_process_id(db: Session, user_id: int, process_id: int):
    """Busca a relação de processo-usuario pelas suas chaves primarias e retorna a relação"""
    return (
        db.query(ProcessUser)
        .filter((ProcessUser.user_id == user_id) & (ProcessUser.process_id == process_id))
        .first()
    )


def get_process_user_by_user_id_all(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
):
    """Busca todas as relação do usuario com processos e retorna os 100 primeiros
    registro com capacidade para ir seguindo a busca"""
    return (
        db.query(ProcessUser)
        .filter(ProcessUser.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_process_user_by_process_id_all(
    db: Session, process_id: int, skip: int = 0, limit: int = 100
):
    """Busca todas as relação do processo com usuarios e retorna os 100 primeiros
    registro com capacidade para ir seguindo a busca"""
    return (
        db.query(ProcessUser)
        .filter(ProcessUser.process_id == process_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_all_process_user(db: Session, skip: int = 0, limit: int = 100):
    """Busca todas as relação de usuario-processo e retorna os 100 primeiros
    registro com capacidade para ir seguindo a busca"""
    return db.query(ProcessUser).offset(skip).limit(limit).all()


def create_process_user(db: Session, process_user: schemas.ProcessUserCreate):
    """Cria uma relação de processo com usuario"""
    db_process_user = ProcessUser(
        user_id=process_user.user_id, process_id=process_user.process_id
    )
    db.add(db_process_user)
    db.commit()
    db.refresh(db_process_user)
    return db_process_user


def delete_process_user(db: Session, user_id: int, process_id: int):
    """Se a relação existir, deleta a relação do banco"""
    
    db_process_user = (
        db.query(ProcessUser)
        .filter((ProcessUser.user_id == user_id) & (ProcessUser.process_id == process_id))
        .first()
    )

    if db_process_user:
        db.delete(db_process_user)
        db.commit()

    return db_process_user

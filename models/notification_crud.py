from sqlalchemy.orm import Session
from database import schemas
from database.database import Base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Notification(Base):
    """Classe que trabalha a tabela de notificações
    e também contém um campo com as evidencia que estão relacionadas a ela
    """

    __tablename__ = "notification"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    typeOfEvent = Column(String(30), default=" ")
    title = Column(String(100))
    mensage = Column(String(400))
    addressed = Column(Integer, ForeignKey("user.id"))
    sender = Column(Integer, ForeignKey("user.id"))
    is_visualized = Column(Boolean, default=False)


def get_notification(db: Session, id: int):
    """Busca no banco ao pedido de evidencia pelo id e retorna ela"""
    return db.query(Notification).filter(Notification.id == id).first()


def get_all_notification(db: Session, skip: int = 0, limit: int = 100):
    """Busca no banco todos os pedidos de evidencia, porém limitando a busca a 100 por vez"""
    return db.query(Notification).offset(skip).limit(limit).all()


def get_not_visualized_notification(db: Session, user_id: int) -> schemas.Notification:
    """Busca no banco todos os pedidos de evidencia, porém limitando a busca a 100 por vez"""
    return (
        db.query(Notification).where(Notification.addressed == user_id).where(Notification.is_visualized == False
        ).order_by(Notification.id)
        .all()
    )


def create_notification(db: Session, notification: schemas.NotificationCreate) -> schemas.Notification:
    """Cria um novo pedido de evidencia no banco"""
    db_notification = Notification(
        typeOfEvent=notification.typeOfEvent,
        title=notification.title,
        mensage=notification.mensage,
        addressed=notification.addressed,
        sender=notification.sender,
        is_visualized=notification.is_visualized,
    )
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification


def update_notification(db: Session, notification: schemas.Notification):
    """Se o pedido de evidencia existir, altera ele no banco"""
    db_notification = (
        db.query(Notification).filter(Notification.id == notification.id).first()
    )

    if db_notification:
        db_notification.typeOfEvent = (notification.typeOfEvent,)
        db_notification.title = (notification.title,)
        db_notification.mensage = (notification.mensage,)
        db_notification.addressed = (notification.addressed,)
        db_notification.sender = (notification.sender,)
        db_notification.is_visualized = notification.is_visualized
        db.commit()
        db.refresh(db_notification)

    return db_notification


def delete_notification(db: Session, id: int):
    """Se o pedido de evidencia existir, deleta ele do banco"""
    db_notification = db.query(Notification).filter(Notification.id == id).first()

    if db_notification:
        db_notification.is_visualized = True
        db.commit()
        db.refresh(db_notification)

    return db_notification


def visualized_notification(db: Session, id: int):
    """Se o pedido de evidencia existir, deleta ele do banco"""
    db_notification = (
        db.query(Notification).filter(Notification.id == id).first()
    )

    if db_notification:
        db_notification.is_visualized = True
        db.commit()

    return db_notification

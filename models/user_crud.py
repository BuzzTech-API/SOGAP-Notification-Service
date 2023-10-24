from fastapi import HTTPException
from sqlalchemy.orm import Session
from database import schemas
from database.database import Base, get_db
from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import relationship, Mapped
from typing import List
from models import process_crud, step_crud, process_user_crud, user_step_crud, request_for_evidence_crud


class User(Base):

    """Aqui é criado a tabela de Usuario que será iniciada no banco
    aqui tem todos os seus atributos além de 2 campos extras que ajudam na hora de fazer as buscas no banco que são os
    relationship retorna uma lista de item, o process é classe ProcessUser e o steps é da classe StepUser
    """

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(60))
    email = Column(String(64), unique=True, index=True)
    password = Column(String(64))
    is_2fa_enable = Column(Boolean, default=False) # Chave booleana para sabe se a autenticação em 2 fatores está habilitada
    secret_key_2fa = Column(String, nullable=True) # Chave secreta gerada para o usuário
    role = Column(String(60))
    team = Column(String(60))
    is_active = Column(Boolean, default=True)
    processes: Mapped[List[process_user_crud.ProcessUser]] = relationship(
        back_populates="user"
    )
    steps: Mapped[List[user_step_crud.UserStep]] = relationship(back_populates="user")
    requests = relationship(request_for_evidence_crud.RequestForEvidence)

#Função para pegar a chave secreta no banco através do ID do usuario.
def get_secret_key(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if user:
        return user.secret_key_2fa
    return None

#Função para salvar a chave secreta no banco através do ID do usuario.
def save_secret_key(db: Session, id:int, secret_key: str):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.secret_key_2fa = secret_key
        db.commit()
        db.refresh(user)

def enable_2fa_first_auth(db: Session, id:int):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.is_2fa_enable=True
        db.commit()
        db.refresh(user)

def disable_2fa(db: Session, id:int):
    user = db.query(User).filter(User.id == id).first()
    if user:
        user.is_2fa_enable=False
        db.commit()
        db.refresh(user)

def get_user(db: Session, id: int):
    """Recebe uma sessão do banco e id e realiza a busca no banco, retornando esse usuário"""
    return db.query(User).filter(User.id == id).first()


def get_user_by_email(db: Session, email: str):
    """Recebe uma sessão do banco e email e realiza a busca no banco, retornando o usuário com esse email"""
    return db.query(User).filter(User.email == email).first()


def get_all_user(db: Session, skip: int = 0, limit: int = 100):
    """Recebe uma sessão do banco, podendo ser utilizando skip e o limit para paginação, por padrão ele busca na tabela usuarios e pega os 100 primeiros usuarios e retorna eles"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    """Recebe uma sessão do banco e a class UserCreate com os dados de criação de um Usuário e adiciona no banco e salva as alteraçãos e atualiza o db_user atribuindo a ele o id que foi gerado no banco e retorna ele com o id dele"""
    db_user = User(
        email=user.email,
        name=user.name,
        password=user.password,
        is_2fa_enable =False,
        secret_key_2fa = '',
        role=user.role,
        team=user.team,
        is_active=user.is_active,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: schemas.User):
    """Recebe uma sessão do banco e o Usuario completo para alteração, primeiro ele chega se aquele usuário existe no banco depois altera todos os campos com o que recebeu do esquema e atualiza o db_user e retorna ele"""
    db_user = db.query(User).filter(User.id == user.id).first()

    if db_user:
        db_user.email = user.email
        db_user.name = user.name
        db_user.password = user.password
        db_user.is_2fa_enable =user.is_2fa_enable
        db_user.cargo = user.cargo
        db_user.team = user.team
        db_user.is_active = user.is_active
        db.commit()
        db.refresh(db_user)

    return db_user


def delete_user(db: Session, id: int):
    """Recebe o sessão do banco e o id do usuario a ser deletado, primeiro realiza a busca dele no banco, se ele existir, o deleta e salva a alteração no banco"""
    db_user = db.query(User).filter(User.id == id).first()

    if db_user:
        db.delete(db_user)
        db.commit()

    return db_user

def get_user_related_data(db: Session, user_id: int):
    user = get_user(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Esse usuário não existe")
    
    processes_list = []
    steps_list = []
    requests_list = []

    for request in user.requests:
            if request.is_actived==False:
                continue
            evidences_list = []
            for evidence in request.evidences:
                evidences_dict = {
                    'link': evidence.link,
                    'idRequestForEvidence': evidence.idRequestForEvidence,
                    'deliveryDate': evidence.deliveryDate.isoformat(),
                    'id': evidence.id
                }
                evidences_list.append(evidences_dict)
            requests_dict = {
                'requiredDocument': request.requiredDocument,
                'description': request.description,
                'step_id': request.step_id,
                'user_id': request.user_id,
                'evidenceValidationDate': request.evidenceValidationDate.isoformat(),
                'deliveryDate': request.deliveryDate.isoformat(),
                'is_validated': request.is_validated,
                'is_actived': request.is_actived,
                'id': request.id,
                'evidences': evidences_list
            }
            
            step = step_crud.get_step(db=db, id=request.step_id)
            if step.is_active == False: 
                continue
            if step.process.is_active == True:
                processes_dict = {
                    'title': step.process.title,
                    'description': step.process.description,
                    'objective': step.process.objective,
                    'endingDate': step.process.endingDate.isoformat(),
                    'createDate': step.process.createDate.isoformat(),
                    'lastUpdate': step.process.lastUpdate.isoformat(),
                    'is_active': step.process.is_active,
                    'priority': step.process.priority,
                    'status': step.process.status,
                    'id': step.process.id,
                    }
                try:
                    processes_list.index(processes_dict)
                except ValueError:    
                    processes_list.append(processes_dict)
            requests_list.append(requests_dict)

    for process_user in user.processes:
        process = process_user.process
        if process.is_active ==False:
            continue

        processes_dict = {
            'title': process.title,
            'description': process.description,
            'objective': process.objective,
            'endingDate': process.endingDate.isoformat(),
            'createDate': process.createDate.isoformat(),
            'lastUpdate': process.lastUpdate.isoformat(),
            'is_active': process.is_active,
            'priority': process.priority,
            'status': process.status,
            'id': process.id,
            }
        try:
            processes_list.index(processes_dict)
        except ValueError:    
            processes_list.append(processes_dict)


    for user_step in user.steps:
        step = user_step.step
        if step.is_active == False: 
            continue
        if step.process.is_active == True:
            processes_dict = {
                'title': step.process.title,
                'description': step.process.description,
                'objective': step.process.objective,
                'endingDate': step.process.endingDate.isoformat(),
                'createDate': step.process.createDate.isoformat(),
                'lastUpdate': step.process.lastUpdate.isoformat(),
                'is_active': step.process.is_active,
                'priority': step.process.priority,
                'status': step.process.status,
                'id': step.process.id,
                }
            try:
                processes_list.index(processes_dict)
            except ValueError:    
                processes_list.append(processes_dict)
        
        steps_dict = {
            'name': step.name,
            'endDate': step.endDate.isoformat(),
            'endingDate': step.endingDate.isoformat(),
            'process_id': step.process_id,
            'objective': step.objective,
            'priority': step.priority,
            'order': step.order,
            'is_active': step.is_active,
            'id': step.id
        }
        steps_list.append(steps_dict)


        
            
        
        

    data = {"processes": processes_list,
            "steps": steps_list,
            "requests": requests_list}


    return data
from models.ConnectionManager import ConnectionManager
from sqlalchemy.orm import Session
from database import schemas
from models.process_crud import Process, Step
from models.request_for_evidence_crud import RequestForEvidence
from models import notification_crud
from models import validation_crud


async def handle_mensage(connectionManager: ConnectionManager, db: Session, data):
    if data['event'] == "Invalidar evidência":
        process = db.query(Process).filter(Process.id == data['data']['process_id']).first()
        step = db.query(Step).filter(Step.id == data['data']['step_id']).first()
        requestForEvidence = (
            db.query(RequestForEvidence)
            .filter(RequestForEvidence.id == data['data']['request_for_evidence_id'])
            .first()
        )

        newNotificationData = {
            "typeOfEvent": "Invalidar Evidencia",
            "title": "Evidência "
            + requestForEvidence.requiredDocument
            + " invalidada do Processo "
            + process.title
            + ", Etapa "
            + step.name,
            "mensage": data['data']['reason'],
            "addressed": requestForEvidence.user_id,
            "sender": data['data']['sender'],
            "is_visualized": False,
        }
        create_notification = notification_crud.create_notification(
            db=db, notification=schemas.NotificationCreate(**newNotificationData)
        )
        validation_dict = {
            "id": 0,
            "evidence_id": data['data']['evidence_id'],
            "reason": data['data']['reason'],
            "user_id": data['data']['sender'],
            "is_validated": False
        }
        create_validation_item = validation_crud.create_validation(db=db, validation=schemas.ValidationCreate(**validation_dict))
        validation_dict['id']=create_validation_item.id
        
        notification_dict = {
                'id': create_notification.id,
                'typeOfEvent':create_notification.typeOfEvent,
                'title':create_notification.title,
                'mensage':create_notification.mensage,
                'addressed':create_notification.addressed,
                'sender':create_notification.sender,
                'is_visualized':create_notification.is_visualized,
            }   

        mensagem = {
            "notification": notification_dict,
            "validation": validation_dict
        }    
        await connectionManager.send_invalited_mensage(
            message=mensagem, user_id=requestForEvidence.user_id
        )

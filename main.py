from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    WebSocket,
    WebSocketException,
    WebSocketDisconnect,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from database import schemas
from sqlalchemy.orm import Session
from models import notification_crud, JWTtoken, user_crud
from database.database import get_db
from typing import Annotated, Optional
from models.ConnectionManager import ConnectionManager
import json
from models import event_handle


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost/"],  # Ou especifique origens específicas
    allow_credentials=["*"],
    allow_methods=["*"],  # Ou especifique métodos específicos (GET, POST, etc.)
    allow_headers=["*"],  # Ou especifique cabeçalhos específicos
)



#email



## Evidencias rotas

async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie(..., alias='access_token')] = None,
    db: Session = Depends(get_db),
):
    if session is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    verify_token = JWTtoken.verify_token(token=session, credentials_exception=WebSocketException(code=status.WS_1008_POLICY_VIOLATION, reason='token invalid'), db=db)
    
    return verify_token



manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(

    websocket: WebSocket,
    user: Annotated[schemas.User, Depends(get_cookie_or_token)],
    db: Session = Depends(get_db)
):
    await websocket.accept()
    myId = websocket.cookies.get('myId')
    access_token = websocket.cookies.get('access_token')
    websocketUser = {
        "websocket": websocket,
        "user":user
    }
    if user:
        await manager.connect(websocketUser)
        for item in notification_crud.get_not_visualized_notification(db=db, user_id=user.id):
            notification_dict = {
                'id': item.id,
                'typeOfEvent':item.typeOfEvent,
                'title':item.title,
                'mensage':item.mensage,
                'addressed':item.addressed,
                'sender':item.sender,
                'is_visualized':item.is_visualized,
            }
            send_dict={
                'notification': notification_dict
            }
            await manager.send_personal_message(send_dict, websocketUser)
        try:
            while True:
                data = await websocketUser['websocket'].receive_json()
                await event_handle.handle_mensage(connectionManager=manager, db=db, data=data)
        except WebSocketDisconnect:
            await manager.disconnect(websocketUser)

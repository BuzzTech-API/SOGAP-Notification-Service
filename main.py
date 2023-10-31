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
from database.schemas import User, WebSocketUser
from sqlalchemy.orm import Session
from models import notification_crud, JWTtoken
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




manager = ConnectionManager()

async def get_cookie_or_token(
    websocket: WebSocket,
    session: Annotated[str | None, Cookie(..., alias='access_token')] = None,
    db: Session = Depends(get_db)
):
    credential = HTTPException(
                status_code = status.WS_1008_POLICY_VIOLATION,
                detail="Token Invalid",
            )
    if session is None:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    return JWTtoken.verify_token(token=(session), db=db, credentials_exception=credential)


@app.websocket("/ws")
async def websocket_endpoint(
    user: Annotated[User, Depends(get_cookie_or_token)], websocket: WebSocket, db: Session = Depends(get_db)
):
    
    websocketUser = WebSocketUser(user=user, websocket=websocket)
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
            await manager.send_personal_message(notification_dict, websocketUser)
        try:
            while True:
                data = await websocketUser.websocket.receive_json()
                await event_handle.handle_mensage(connectionManager=manager, db=db, data=data)
        except WebSocketDisconnect:
            manager.disconnect(websocketUser)

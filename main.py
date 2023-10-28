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
from models import notification_crud, JWTtoken
from database.database import get_db
from typing import Annotated, Optional
import json
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou especifique origens específicas
    allow_methods=["*"],  # Ou especifique métodos específicos (GET, POST, etc.)
    allow_headers=["*"],  # Ou especifique cabeçalhos específicos
)



#email



## Evidencias rotas



class ConnectionManager:
    def __init__(self):
        self.active_connections: list[schemas.WebSocketUser] = []

    async def connect(self, websocket: schemas.WebSocketUser):
        await websocket.websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: schemas.WebSocketUser):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: schemas.WebSocketUser):
        await websocket.websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)


manager = ConnectionManager()



@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket, db: Session = Depends(get_db)
):
    credential = HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail="Token Invalid",
            )
    user = JWTtoken.verify_token(token=websocket.cookies.get('access_token'), db=db, credentials_exception=credential)
    
    websocketUser = schemas.WebSocketUser(user=user, websocket=websocket)
    
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
                await manager.send_personal_message(f"You wrote: {data}", websocketUser)
                await manager.broadcast(f"Client says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocketUser)
            await manager.broadcast(f"Client #{websocketUser.websocket.client} left the chat")

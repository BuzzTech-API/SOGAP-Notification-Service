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
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated, Optional
from sqlalchemy.orm import Session
from database import schemas
from models import JWTtoken, oauth2
from database.database import get_db


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Ou especifique origens específicas
    allow_methods=["*"],  # Ou especifique métodos específicos (GET, POST, etc.)
    allow_headers=["*"],  # Ou especifique cabeçalhos específicos
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[schemas.WebSocketUser] = []

    async def connect(self, websocket: schemas.WebSocketUser):
        await websocket.websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: schemas.WebSocketUser):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: schemas.WebSocketUser):
        await websocket.websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)


manager = ConnectionManager()



@app.websocket("/ws")
async def websocket_endpoint(
    *, websocket: WebSocket, db: Session = Depends(get_db)
):
    credential = HTTPException(
                status_code = status.HTTP_403_FORBIDDEN,
                detail="Token Invalid",
            )
    user = JWTtoken.verify_token(token=websocket.cookies.get('access_token'), db=db, credentials_exception=credential)
    
    websocketUser = schemas.WebSocketUser(user=user, websocket=websocket)
    
    print(websocketUser)
    if user:
        await manager.connect(websocketUser)
        try:
            while True:
                data = await websocketUser.websocket.receive_text()
                await manager.send_personal_message(f"You wrote: {data}", websocketUser)
                await manager.broadcast(f"Client says: {data}")
        except WebSocketDisconnect:
            manager.disconnect(websocketUser)
            await manager.broadcast(f"Client #{websocketUser.websocket.client} left the chat")

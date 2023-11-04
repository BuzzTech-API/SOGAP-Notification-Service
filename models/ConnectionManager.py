from pydantic import BaseModel
from models import user_crud
from fastapi import WebSocket

import json
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[{}] = []

    async def connect(self, websocketUser: {}):
        #await websocketUser.websocket.accept()
        self.active_connections.append(websocketUser)

    async def disconnect(self, websocketUser: {}):
        self.active_connections.remove(websocketUser)

    async def send_personal_message(self, message, websocketUser: {}):
        await websocketUser['websocket'].send_json(message)

    async def send_personal_broadcast(self, message, user_id: int):
        for connection in self.active_connections:
            if user_id == connection.user.id:
                await connection['websocket'].send_json(message)

    async def send_invalited_mensage(self, message, user_id: int):
        for connection in self.active_connections:
            if user_id == connection['user'].id:
                await connection['websocket'].send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)


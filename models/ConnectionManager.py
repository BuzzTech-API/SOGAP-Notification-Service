from database import schemas
import json
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[schemas.WebSocketUser] = []

    async def connect(self, websocket: schemas.WebSocketUser):
        await websocket.websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: schemas.WebSocketUser):
        await websocket.websocket.close()
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message, websocket: schemas.WebSocketUser):
        await websocket.websocket.send_json(message)

    async def send_personal_broadcast(self, message, user_id: int):
        for connection in self.active_connections:
            if user_id == connection.user.id:
                await connection.websocket.send_json(message)

    async def send_invalited_mensage(self, message, user_id: int):
        for connection in self.active_connections:
            if user_id == connection.user.id:
                await connection.websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.websocket.send_text(message)


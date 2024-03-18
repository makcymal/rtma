from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from python_freeipa import ClientMeta


from backend_app.utils import create_access_token, create_refresh_token
from backend_app.models import User

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()


@app.get("/")
async def get():
    return 0


@app.post('/login')
async def login(user: User):
    client = ClientMeta('ipa1-hlit.jinr.ru')
    client.login(user.login, user.password)
    user_data = client.user_show(user.login)['result']
    user_public_data = {"id": user_data['uid'], 'name': user_data['displayname'], 'mail': user_data['mail'],
                        'homedirectory': user_data['homedirectory']}
    # добавить обработку ошибки

    return {
        "access_token": create_access_token(user_public_data),
        "refresh_token": create_refresh_token(user_public_data),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"You wrote: {data}", websocket)
            await manager.broadcast(f"Client #{client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client #{client_id} has left the channel")



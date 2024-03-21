import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Cookie
from fastapi import status, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from python_freeipa import ClientMeta
from python_freeipa.exceptions import InvalidSessionPassword
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from starlette.responses import JSONResponse, Response

from agg_backend_app import config
from auth_utils import encode_jwt, generate_cookie_session_id, decode_jwt

from models import User

app = FastAPI()

http_bearer = HTTPBearer()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082"
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
    "http://127.0.0.1",
    "http://localhost/",
    "http://localhost:8080/",
    "http://localhost:8081/",
    "http://localhost:8082/"
    "http://127.0.0.1:8080/",
    "http://127.0.0.1:8081/",
    "http://127.0.0.1:8082/",
    "http://127.0.0.1/"
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie"],
)


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
    return {"hello": "hello"}


@app.post('/api/token/login')
async def login(user: User):
    try:
        client = ClientMeta('ipa1-hlit.jinr.ru')
        client.login(user.login, user.password)
    except InvalidSessionPassword:
        return {
            "status": "ERROR",
            "data": None,
            "details": "Invalid login or password"
        }
    user_data = client.user_show(user.login)['result']
    user_public_data = {"sub": user_data["uid"][0], "id": user_data['uid'][0], 'name': user_data['displayname'][0], 'mail': user_data['mail'][0],
                        'homedirectory': user_data['homedirectory'][0]}

    access_token = encode_jwt(user_public_data)

    expires = datetime.datetime.utcnow() + datetime.timedelta(minutes=config.settings.auth_jwt.access_token_expire_min)

    content = {
        "status": "OK",
        "data": None,
        "details": "user authorized"
    }

    response = JSONResponse(content=content)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True, secure=True, samesite='none', path="/",
                        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    return response


@app.post('/api/token/logout')
async def logout():
    content = {
        "status": "OK",
        "data": None,
        "details": "user logged out"
    }

    response = JSONResponse(content=content)

    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)

    response.set_cookie(
        key="access_token",
        value="",
        secure=True,
        httponly=True,
        samesite='none',
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        path="/"
    )
    return response


@app.get('/check-cookie-login')
async def check_cookie_login(token: Optional[str] = Cookie(alias="access_token")):
    print(token)
    token = token.split()[1]
    public_data = decode_jwt(token)
    del public_data['sub']
    return {
        "status": "OK",
        "data": public_data,
        "details": "user authorized"
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



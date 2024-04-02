import datetime
import json
import logging
import random
import threading

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
    Depends,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from jwt import InvalidTokenError
from python_freeipa import ClientMeta
from python_freeipa.exceptions import InvalidSessionPassword
from fastapi.security import HTTPBearer
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
# import redis.asyncio as aioredis
import asyncio as aio

from backend_app import config
from backend_app.utils.auth_utils import encode_jwt, decode_jwt

from models import User

logger = logging.getLogger(__name__)

app = FastAPI()

http_bearer = HTTPBearer()

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:8081",
    "http://localhost:8082",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:8081",
    "http://127.0.0.1:8082",
    "http://127.0.0.1",
    "http://localhost/",
    "http://localhost:8080/",
    "http://localhost:8081/",
    "http://localhost:8082/",
    "http://127.0.0.1:8080/",
    "http://127.0.0.1:8081/",
    "http://127.0.0.1:8082/",
    "http://127.0.0.1/",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Set-Cookie"],
)


@app.get("/")
async def get():
    return {"hello": "hello"}


@app.post("/api/token/login")
async def login(user: User):
    try:
        client = ClientMeta("ipa1-hlit.jinr.ru")
        client.login(user.login, user.password)
    except InvalidSessionPassword:
        return {"status": "ERROR", "data": None, "details": "Invalid login or password"}
    user_data = client.user_show(user.login)["result"]
    user_public_data = {
        "sub": user_data["uid"][0],
        "id": user_data["uid"][0],
        "name": user_data["displayname"][0],
        "mail": user_data["mail"][0],
        "homedirectory": user_data["homedirectory"][0],
    }

    access_token = encode_jwt(user_public_data)

    expires = datetime.datetime.utcnow() + datetime.timedelta(
        minutes=config.settings.auth_jwt.access_token_expire_min
    )

    content = {"status": "OK", "data": None, "details": "user authorized"}

    response = JSONResponse(content=content)
    response.set_cookie(
        key="access_token",
        value=f"{access_token}",
        httponly=True,
        secure=True,
        samesite="none",
        path="/",
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
    )
    return response


@app.post("/api/token/logout")
async def logout():
    content = {"status": "OK", "data": None, "details": "user logged out"}

    response = JSONResponse(content=content)

    # expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=5)

    response.delete_cookie(
        key="access_token", secure=True, httponly=True, samesite="none", path="/"
    )
    return response


def get_data_from_jwt_cookie(request: Request):
    token = request.cookies.get("access_token")
    try:
        public_user_data = decode_jwt(token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authorized or invalid token",
        )
    del public_user_data["sub"]
    return public_user_data


@app.get("/check-cookie-login")
async def check_cookie_login(user_data: dict = Depends(get_data_from_jwt_cookie)):
    return {"status": "OK", "data": user_data, "details": "user authorized"}


header_sended = False
user_subscribed = False
user_msg = ""
from test_data import *
import asyncio
@app.websocket("/echo")
async def websocket_echo(ws: WebSocket):
    global user_subscribed, user_msg
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            print(msg.split("?"))
            user_msg = msg
            if user_msg.split("?")[0] == 'head':
                await ws.send_json(HEADERS)
                user_msg = 'head'
            elif user_msg.split("?")[0] == 'lsob':
                await ws.send_json({
    "header": "lsob",
    "batches": ["gvr:cascade", "gvr:dgx", "gvr:gpu", "gvr:icelake", "gvr:knl", "hlit:wn", "jhub", "service", "storage", "vm"]})
            elif user_msg.split("?")[0] == 'mstd':
                user_subscribed = True
            if user_msg.split("?")[0] == 'mstd' and user_msg.split("?")[1] == 'gvr:dgx':
                await ws.send_json(COMP_NODES)
                print('data_is_sending')
                COMP_NODES['cpu']['user'] = random.randint(0, 100)
                COMP_NODES['header'] = random.choice(["mstd!gvr:knl!n01p001!1711098779", "mstd!gvr:knl!n01p002!1711098779",
                                                      "mstd!gvr:knl!n01p003!1711098779", "mstd!gvr:knl!n01p004!1711098779",
                                                      "mstd!gvr:knl!n01p005!1711098779", "mstd!gvr:knl!n01p006!1711098779",
                                                      "mstd!gvr:knl!n01p007!1711098779", "mstd!gvr:knl!n01p008!1711098779",
                                                      "mstd!gvr:knl!n01p009!1711098779", "mstd!gvr:knl!n01p010!1711098779"
                                                      "mstd!gvr:knl!n01p011!1711098779", "mstd!gvr:knl!n01p012!1711098779",
                                                      "mstd!gvr:knl!n01p013!1711098779", "mstd!gvr:knl!n01p014!1711098779",
                                                      "mstd!gvr:knl!n01p015!1711098779", "mstd!gvr:knl!n01p016!1711098779",
                                                      "mstd!gvr:knl!n01p016!1711098779", "mstd!gvr:knl!n01p017!1711098779",
                                                      "mstd!gvr:knl!n01p018!1711098779", "mstd!gvr:knl!n01p019!1711098779"])
            elif user_msg.split("?")[0] == 'mstd' and user_msg.split("?")[1] == 'gvr:gpu':
                await ws.send_json(COMP_NODES)
                print('111data_is_sending1')
                COMP_NODES['cpu']['user'] = random.randint(0, 100)
                COMP_NODES['header'] = random.choice(
                    ["mstd!gvr:knl!n01p001!1711098779", "mstd!gvr:knl!n01p002!1711098779",
                     "mstd!gvr:knl!n01p003!1711098779", "mstd!gvr:knl!n01p004!1711098779",
                     "mstd!gvr:knl!n01p005!1711098779"])
            await aio.sleep(0.5)
    except:
        pass


class ConnManager:
    def __init__(self) -> None:
        pass
    
    
class QueryManager:
    def __init__(self) -> None:
        pass
    
    
class ResponsesRepo:
    def __init__(self) -> None:
        pass


# Globals
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 42401
redis_client = None
conn_mgr = ConnManager()
query_mgr = QueryManager()
responses = ResponsesRepo()


# in case @app.websocket fails for some reason use
# @app.websocket_route("/ws")
@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await conn_mgr.connect(ws)
    try:
        while True:
            query = ws.receive_text()
            query_mgr.register(ws, query)
    except WebSocketException:
        query_mgr.unregister(ws)
        await conn_mgr.disconnect(ws)


# @app.on_event("startup")
# async def redis_startup():
#     global redis_client
#     redis_client = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT)
#     threading.Thread(target=redis_listen, daemon=True).start()


def redis_listen():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("channel_signal")
    
    for msg in pubsub.listen():
        if msg["type"] == "message":
            data = json.loads(msg["data"])
            

import datetime
import logging

from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
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

from backend_app import config
from backend_app import conn_broker
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


query_manager = conn_broker.QueryManager()


# in case @app.websocket fails for some reason use
# @app.websocket_route("/ws")
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.debug(f"{websocket.client} connected")
    try:
        while True:
            query = await websocket.receive_text()
            logger.debug(f"{websocket.client} queried: {query}")
            response = await query_manager[query]
            logger.debug(f"sending response to {websocket.client}: {response}")
            await websocket.send(response)
    except WebSocketDisconnect:
        logger.debug(f"{websocket.client} disconnected")

import struct
import secrets
import logging
import asyncio as aio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer

from router import router


logger = logging.getLogger(__name__)

SENSOR_DISCONNECTED = f"{secrets.randbits(32)}"


async def recvall(reader: aio.StreamReader) -> str:
    raw_size = await reader.read(4)
    if raw_size == b"":
        return SENSOR_DISCONNECTED
    size = struct.unpack("i", raw_size)[0]

    data = await reader.read(size)
    data = data.decode(encoding="utf-8")
    return data


async def sendall(data: str, writer: aio.StreamWriter):
    data = data.encode(encoding="utf-8")
    size = struct.pack("i", len(data))

    writer.write(size)
    await writer.drain()

    writer.write(data)
    await writer.drain()


async def sensor_handler(reader: aio.StreamReader, writer: aio.StreamWriter):
    peername = writer.get_extra_info("peername")
    # peername = get_sensor_name(peername)
    logger.info(f"Sensor {peername} connected to cluster_server")

    while True:
        if data := await recvall(reader, writer) == SENSOR_DISCONNECTED:
            logger.warning(f"Sensor {peername} disconnected")
            break
        logger.debug(f"Sensor {peername} sent data of size {len(data)}")


# https://stackoverflow.com/questions/77674952/how-to-run-fastapi-app-and-tcp-server-as-async-tasks-within-the-same-fastapi-eve
@asynccontextmanager
async def startup_event(app: FastAPI):
    # start server listening to cluster
    cluster_server = await aio.start_server(
        sensor_handler, port="42400", reuse_port=True
    )
    aio.create_task(cluster_server.serve_forever())

    yield

    # graceful shutdown
    ...


app = FastAPI(lifespan=startup_event)

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

# https://stackoverflow.com/questions/76231804/fastapi-how-to-modularize-code-into-multiple-files-with-access-to-app-decorators
app.include_router(router)

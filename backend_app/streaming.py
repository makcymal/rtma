import json
import logging
import secrets
import asyncio as aio
import struct
from fastapi import APIRouter, WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)


class ClientsMgr:
    def __init__(self):
        self.ls = {}
    
    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.ls[ws] = ""
        
    def update(self, ws: WebSocket, query: str):
        self.ls[ws] = query
        
    def disconnect(self, ws: WebSocket):
        del self.ls[ws]
        

class SensorsMgr:
    def __init__(self):
        self.ls = {}
        self.addr2id = {}
        self.id2addr = {}
        self.specs = {}

    def insert(self, addr, specs: dict):
        id = specs.pop("id")
        self.addr2id[addr] = id
        self.id2addr[id] = addr
        self.specs[addr] = specs


class QueriesMgr:
    def __init__(self):
        with open("query.standard.json", "r") as std_file:
            self.std = json.load(std_file)
        with open("query.extended.json", "r") as ext_file:
            self.ext = json.load(ext_file)


class ResponsesMgr:
    def __init__(self):
        self.repo = {}

    def insert(self, resp: dict):
        id = resp.pop("id")
        batch, label, mark, time = id
        self.repo[batch][label] = resp


PEER_DISCONNECTED = f"{secrets.randbits(32)}"
SENSORS_PORT = 42400
m_clients = ClientsMgr()
m_sensors = SensorsMgr()
m_queries = QueriesMgr()
m_responses = ResponsesMgr()
ws_router = APIRouter()


# in case @app.websocket fails for some reason use
# @app.websocket_route("/ws")
@ws_router.websocket("/ws")
async def handle_client(ws: WebSocket):
    # websocket connecting
    await m_clients.connect(ws)
    
    while True:
        try:
            query = await ws.receive_text()
            # trigger sending query to appropriate sensor
        except WebSocketDisconnect:
            m_clients.disconnect(ws)


async def get_sensor_server() -> aio.Server:
    return await aio.start_server(handle_sensor, port=SENSORS_PORT, reuse_port=True)


async def handle_sensor(reader: aio.StreamReader, writer: aio.StreamWriter):
    addr = writer.get_extra_info("addr")
    await sensor_recv_specs(reader, addr)
    print(f"Sensor {addr}: {m_sensors.addr2id[addr]} connected")

    while True:
        if (response := await recvall(reader)) == PEER_DISCONNECTED:
            break
        # trigger sending response to client
        m_responses.insert(json.loads(response))


async def sensor_recv_specs(reader: aio.StreamReader, addr):
    # save specs
    specs = json.dumps(await recvall(reader))
    m_sensors.insert(addr, specs)
    # add batch to responses so it's possible to insert to dict without checks
    batch = specs["header"].split("!")[0]
    if batch not in m_responses.repo:
        m_responses.repo[batch] = {}


async def sensor_send_queries(writer: aio.StreamWriter):
    pass


class QueryManager:

    __slots__ = ("queries", "sockets", "_query_map", "_query_counter")

    def __init__(self):
        self.queries = set()
        self.sockets = set()
        self._query_map = {}
        self._query_counter = {}
        logger.debug(f"Created empty {self.__class__.__name__}")

    def _add_query(self, ws: WebSocket, query: str):
        # стандартный майкрософтовский энвелоуп
        self._query_map[ws] = query
        self.queries.add(query)
        if query not in self._query_counter:
            self._query_counter[query] = 0
            logger.debug(f"Query {query} added")
        self._query_counter[query] += 1
        logger.debug(f"Query {query} counter increased: {self._query_counter[query]}")

    def _remove_query(self, ws: WebSocket):
        if ws not in self._query_map:
            return

        old_query = self._query_map[ws]
        self._query_counter[old_query] -= 1
        logger.debug(f"Query {old_query} decreased: {self._query_counter[old_query]}")
        if self._query_counter[old_query] == 0:
            self.queries.remove(old_query)
            logger.debug(f"Query {old_query} removed")

    async def register(self, ws: WebSocket, query: str):
        if ws not in self.sockets:
            await ws.accept()
            self.sockets.add(ws)

        # индиана джонс
        self._remove_query(ws)
        self._add_query(ws, query)

        dump = json.dumps(list(self.queries))
        await broker_conn.sendall(dump)

    def unregister(self, ws: WebSocket):
        self.sockets.remove(ws)
        self._remove_query(ws)
        del self._query_map[ws]


async def recvall(reader: aio.StreamReader) -> str:
    raw_size = await reader.read(4)
    if raw_size == b"":
        return PEER_DISCONNECTED
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

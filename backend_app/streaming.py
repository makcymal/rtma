import json
import logging
import secrets
import asyncio as aio
import struct
from fastapi import APIRouter, WebSocket, WebSocketDisconnect


logger = logging.getLogger(__name__)


class ClientMgr:
    def __init__(self):
        self.ls = {}

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.ls[ws] = ""

    def update(self, ws: WebSocket, query: str):
        self.ls[ws] = query

    def disconnect(self, ws: WebSocket):
        del self.ls[ws]


class SensorMgr:
    def __init__(self):
        self.ls = {}
        self.addr2id = {}
        self.id2addr = {}
        self.specs = {}
        self.batches = 

    def insert(self, addr, specs: dict):
        header = specs.pop("header")
        self.addr2id[addr] = id
        self.id2addr[id] = addr
        self.specs[addr] = specs


class QueryMgr:
    def __init__(self):
        with open("query.standard.json", "r") as std_file:
            self.std = json.loads(std_file)
        with open("query.extended.json", "r") as ext_file:
            self.ext = json.loads(ext_file)

        # all queries existing right now
        self.query_set = set()
        # map websocket -> query
        # needed to delete unused queries, nevermore
        self.query_map = {}
        # map query -> #{how much such a queries exist}
        self.query_cnt = {}

    def insert(self, ws: WebSocket, query: str):
        self.remove(ws)
        # стандартный майкрософтовский энвелоуп
        self.query_map[ws] = query
        self.query_set.add(query)

        if query not in self.query_cnt:
            self.query_cnt[query] = 1
            aio.create_task(extend_sensor(query))
        else:
            self.query_cnt[query] += 1

    def remove(self, ws: WebSocket):
        if ws not in self.query_map:
            return

        old_query = self.query_map[ws]
        self.query_cnt[old_query] -= 1
        if self.query_cnt[old_query] == 0:
            self.query_set.remove(old_query)
            aio.create_task(reduce_sensor())
            
    async def extend_sensor(self, query):
        


class ResponseMgr:
    def __init__(self):
        self.repo = {}

    def insert(self, resp: dict):
        id = resp.pop("id")
        batch, label, mark, time = id
        self.repo[batch][label] = resp


PEER_DISCONNECTED = f"{secrets.randbits(32)}"
SENSORS_PORT = 42400
m_clients = ClientMgr()
m_sensors = SensorMgr()
m_queries = QueryMgr()
m_responses = ResponseMgr()
ws_router = APIRouter()


# in case @app.websocket fails for some reason use
# @app.websocket_route("/ws")
@ws_router.websocket("/ws")
async def handle_client(ws: WebSocket):
    '''
    Client can send one of the followings messages:
    "lsob" - get LiSt Of Batches
    "head?BATCH" - get table HEADer for BATCH
    "mstd?BATCH" - STanDard Monitoring subscribe to BATCH
    "spec?BATCH?LABEL" - get SPECifications of machine with LABEL in BATCH
    "mext?BATCH?LABEL" - EXTended Monitoring to machine with LABEL in BATCH
    "stop" - stop subscription
    '''
    
    # websocket connecting
    await m_clients.connect(ws)

    while True:
        try:
            msg = await ws.receive_text()
            if msg[0] == "?":
                m_queries.insert(ws, msg[1:])
            elif msg[0] == "!":
                m_queries.insert(ws, msg.split("!")[1:])
            elif msg.startswith("lsob"):
                await send_batches_to_client(ws)
            elif msg.startswith("head"):
                await send_table_header_to_client(ws, msg.split('?')[1])
            elif msg.startswith("spec"):
                await send_specs_to_client(ws, msg.split("!")[1:])
            elif msg.startswith("stop"):
                m_queries.remove(ws)

            # trigger sending query to appropriate sensor
        except WebSocketDisconnect:
            m_clients.disconnect(ws) 
            

async def send_batches_to_client(ws: WebSocket):
       


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

import json
import logging
import secrets
import asyncio as aio
import struct
import weakref
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
        self.specs = {}
        self.batches: list[str] = []

    def insert(self, addr, specs: dict):
        header = specs.pop("header")
        mark, batch, label = header.split("!")
        id = f"{batch}!{label}"
        self.specs[id] = specs

        for i in range(len(self.batches)):
            if batch == self.batches[i]:
                break
        else:
            self.batches.append(batch)
            for i in range(len(self.batches) - 2, -1, -1):
                if self.batches[i] > self.batches[i + 1]:
                    self.batches[i : i + 2] = self.batches[i : i + 2][::-1]
                else:
                    break


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
        pass


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
    """
    Client can send one of the followings messages:
    "lsob" - get LiSt Of Batches
    "head?BATCH" - get table HEADer for BATCH
    "mstd?BATCH" - STanDard Monitoring subscribe to BATCH
    "spec?BATCH?LABEL" - get SPECifications of machine with LABEL in BATCH
    "mext?BATCH?LABEL" - EXTended Monitoring to machine with LABEL in BATCH
    "stop" - stop subscription
    """

    # websocket connecting
    await m_clients.connect(ws)
    curr_task = None

    while True:
        try:
            msg = await ws.receive_text()
            if isinstance(curr_task, aio.Task):
                curr_task.cancel()

            match msg[:4]:
                case "lsob":
                    await handle_client_lsob(ws)
                case "head":
                    batch = msg.split("?")[1]
                    await handle_client_head(ws, batch)
                case "mstd":
                    batch = msg.split("?")[1]
                    curr_task = aio.create_task(handle_client_mstd(ws, batch))
                case "spec":
                    batch, label = msg.split("?")[1:3]
                    await handle_client_spec(ws, batch, label)
                case "mext":
                    batch, label = msg.split("?")[1:3]
                    curr_task = aio.create_task(handle_client_mext(ws, batch, label))
                case "stop":
                    pass

            # trigger sending query to appropriate sensor
        except WebSocketDisconnect:
            m_clients.disconnect(ws)


async def handle_client_lsob(ws: WebSocket):
    response = {"header": "lsob", "batches": m_sensors.batches}
    await ws.send_json(response)


async def handle_client_head(ws: WebSocket, batch: str):
    response = {
        "header": f"head!{batch}",
        "fields": {"cpu": [""], "net": [], "mem": [], "dsk": []},
    }


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

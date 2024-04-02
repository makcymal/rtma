import json
import asyncio as aio
import struct
import secrets
from copy import deepcopy as cp
from fastapi import WebSocket
from dataclasses import dataclass


# random string indicating that sensor was disconnected
PEER_DISCONNECTED = f"{secrets.randbits(32)}"


class ClientRepo:
    __slots__ = ("_ls", "queries", "subs")

    def __init__(self) -> None:
        self._ls = set()
        self.queries = {}
        self.subs = {}

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._ls.add(ws)

    def subscribe(self, ws: WebSocket, query: str):
        if self.queries.get(ws, None) == query:
            return

        self.queries[ws] = query
        if query not in self.subs:
            self.subs[query] = set()
        self.subs[query].add(ws)
        queries.insert(query)

    def notify(self, query: str, resp: dict):
        sub: WebSocket
        for sub in self.subs.get(query, []):
            aio.create_task(sub.send_json(resp))

    def unsubscribe(self, ws: WebSocket):
        if ws not in self.queries:
            return

        self.subs[self.queries[ws]].remove(ws)
        del self.queries[ws]
        queries.remove(ws)

    def disconnect(self, ws: WebSocket):
        self.unsubscribe(ws)
        self._ls.remove(ws)


@dataclass(frozen=True, slots=True)
class Sensor:
    reader: aio.StreamReader
    writer: aio.StreamWriter
    specs: dict


class SensorRepo:
    __slots__ = ("_ls", "batches")

    def __init__(self) -> None:
        self._ls = {}
        self.batches = []

    def __iter__(self) -> list[Sensor]:
        return self._ls

    def insert(
        self,
        batch: str,
        label: str,
        reader: aio.StreamReader,
        writer: aio.StreamWriter,
        specs: dict,
    ):
        if batch not in self._ls.keys():
            self._ls[batch] = {}
            self.batches.append(batch)
            responses.add_batch(batch)
        self._ls[batch][label] = Sensor(reader, writer, specs)


class ResponseRepo:
    __slots__ = ("std", "ext")

    def __init__(self) -> None:
        self.std = {}
        self.ext = {}

    def add_batch(self, batch: str):
        self.std[batch] = {}
        self.ext[batch] = {}

    def insert(self, batch: str, label: str, resp: dict):
        proto, _batch, _label, mark, time = resp.pop("header").split("!")[:5]
        if mark == "std":
            header = f"mstd!{batch}!{label}!{time}"
            self.std[batch][label] = {"header": header, **resp}
        elif mark == "ext":
            header = f"mext!{batch}!{label}!{time}"
            self.ext[batch][label] = {"header": header, **resp}
            # someone monitoring the whole batch including current particular machine
            if batch in queries:
                self.std[batch][label] = {
                    "header": header,
                    **self.standartise_response(batch, label, resp),
                }

    def send_last(self, batch: str, label: str):
        clients.notify(batch, self.std[batch][label])
        clients.notify(f"{batch}!{label}", self.ext[batch][label])

    # when sensor sends only extended responses while we need both extended and standard
    # we can reduce amount of information in extended resp to make standard
    def standartise_response(self, batch: str, label: str, resp: dict) -> dict:
        cpu = self._standartise_cpu(resp["cpu"])
        net = self._standartise_net(resp["net"])
        mem = self._standartise_mem(batch, label, resp["mem"])
        dsk = self._standartise_dsk(resp["dsk"])
        return {"cpu": cpu, "net": net, "mem": mem, "dsk": dsk}

    def _standartise_cpu(cpu_percore: list[dict]) -> dict:
        cores = len(cpu_percore)
        if not cores:
            return {}

        cpu: dict = cp(cpu_percore[0])
        cpu_std_fields = set(queries.std["cpu_fields"])
        for field in cpu:
            if field not in cpu_std_fields:
                cpu.pop(field)
            else:
                for i in range(1, cores):
                    cpu[field] += cpu_percore[i][field]
                cpu[field] /= cores

    def _standartise_net(net_pernic: dict) -> dict:
        nics = net_pernic.keys()
        if not nics:
            return {}

        net = cp(net_pernic[nics[0]])
        net_std_fields = set(queries.std["net_fields"])
        for field in net.keys():
            if field not in net_std_fields:
                net.pop(field)
            else:
                for nic in nics:
                    net[field] += net_pernic[nic][field]

        return net

    def _standartise_mem(batch, label, mem_ext: dict) -> dict:
        mem = cp(mem_ext)
        # some fucking hardcode
        for field in ["buffers", "cached", "shared"]:
            mem.pop(field, None)
        if "used" in mem:
            mem["used"] = round(
                mem["used"] / sensors[batch][label]["mem"]["mem_total"] * 100, 1
            )
        if "swap" in mem:
            mem["swap"] = round(
                mem["swap"] / sensors[batch][label]["mem"]["swp_total"] * 100, 1
            )

        return mem

    def _standartise_dsk(dsk_perdisk: dict) -> dict:
        disks = dsk_perdisk.keys()
        if not disks:
            return {}

        dsk = cp(dsk_perdisk[disks[0]])
        dsk_std_fields = set(queries.std["dsk_fields"])
        for field in dsk:
            if field not in dsk_std_fields:
                dsk.pop(field)
            else:
                for disk in disks:
                    dsk[field] += dsk_perdisk[disk][field]

        return dsk


class QueryRepo:
    __slots__ = ("std", "ext", "query_set", "query_cnt")

    def __init__(self) -> None:
        with open("json/query.standard.json", "r") as std_file:
            self.std = json.load(std_file)
            self.std_str = json.dumps(self.std)
        with open("json/query.extended.json", "r") as ext_file:
            self.ext = json.load(ext_file)
            self.ext_str = json.dumps(self.ext)

        # all queries existing right now
        self.query_set = set()
        # map query -> #{how much such a queries exist}
        self.query_cnt = {}

    def __contains__(self, query: str) -> bool:
        return self.query_set.__contains__(query)

    def insert(self, query: str):
        # стандартный майкрософтовский энвелоуп
        self.query_set.add(query)
        if query not in self.query_cnt:
            self.query_cnt[query] = 0
            aio.create_task(self.inject_query(query))
        self.query_cnt[query] += 1

    def remove(self, query: str):
        self.query_cnt[query] -= 1
        if self.query_cnt[query] == 0:
            self.query_set.remove(query)
            aio.create_task(self.seize_query(query))

    async def inject_query(self, query: str):
        tokens = query.split("!")
        if len(tokens) == 1:
            batch = query
            for label in sensors._ls[batch]:
                if f"{batch}!{label}" not in self.query_set:
                    sensor: Sensor = sensors._ls[batch][label]
                    await sendall(self.std_str, sensor.writer)
        else:
            batch, label = tokens[:2]
            sensor: Sensor = sensors._ls[batch][label]
            await sendall(self.ext_str, sensor.writer)

    async def seize_qeury(self, query: str):
        tokens = query.split("!")
        if len(tokens) == 1:
            batch = query
            for label in sensors._ls[batch]:
                if f"{batch}!{label}" not in self.query_set:
                    sensor: Sensor = sensors._ls[batch][label]
                    await sendall("stop", sensor.writer)
        else:
            batch, label = tokens[:2]
            sensor: Sensor = sensors._ls[batch][label]
            if batch in self.query_set:
                await sendall(self.std_str, sensor.writer)
            else:
                await sendall("stop", sensor.writer)


clients = ClientRepo()
sensors = SensorRepo()
responses = ResponseRepo()
queries = QueryRepo()


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

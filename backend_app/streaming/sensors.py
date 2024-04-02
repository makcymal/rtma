import json
import asyncio as aio
from store import sensors, responses, PEER_DISCONNECTED, recvall, sendall


# port used to listen to sensors
SENSORS_PORT = 42400


# entry point for the communication with sensors
async def serve_sensors():
    server = await aio.start_server(handle_sensor, port=SENSORS_PORT, reuse_port=True)
    aio.create_task(server.serve_forever())


# initially recieves sensor specs
# then infinitely waits for responses from sensor
# another function in another event loop sends queries to sensors
async def handle_sensor(reader: aio.StreamReader, writer: aio.StreamWriter):
    # recieving specs
    specs = json.dumps(await recvall(reader))
    proto, batch, label = specs.pop("header").split("!")[:3]
    sensors.insert(batch, label, reader, writer, specs)
    # recieving responses
    while True:
        if (resp := await recvall(reader)) == PEER_DISCONNECTED:
            break
        # trigger sending resp to client
        responses.insert(batch, label, json.load(resp))
        responses.send_last(batch, label)

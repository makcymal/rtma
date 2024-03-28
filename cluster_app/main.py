import time
import json
import struct
import logging
import asyncio as aio

from query import Query
from trackers import all_trackers
import config


logger = logging.getLogger(__name__)

reader: aio.StreamReader
writer: aio.StreamWriter
lock = aio.Lock()
specs: str


async def reconnect():
    global reader, writer
    async with lock:
        if writer.is_closing():
            logger.warning("Connection to backend was suddenly closed")
            if config.ALWAYS_RECONNECT:
                logger.warning("Trying to reconnect")
                while writer.is_closing():
                    try:
                        reader, writer = await aio.open_connection(
                            host=config.HOST_BACKEND,
                            port=config.PORT_BACKEND,
                        )
                    except OSError:
                        pass
                    await aio.sleep(config.RECONNECT_DELAY)
            else:
                logger.critical("ALWAYS_RECONNECT == False, graceful shutdown")
                exit(1)

    logger.info("Reconnected successfully")
    await sendall(specs)


async def recvall() -> str:
    raw_size = await reader.read(4)
    if raw_size == b"":
        return config.BACKEND_DISCONNECT
    size = struct.unpack("i", raw_size)[0]

    data = await reader.read(size)
    data = data.decode(encoding="utf-8")
    return data


async def sendall(data: str):
    data = data.encode(encoding="utf-8")
    size = struct.pack("i", len(data))

    writer.write(size)
    await writer.drain()

    writer.write(data)
    await writer.drain()


async def writing_responses():
    global specs
    # initializing trackers
    trackers = all_trackers()

    # getting specifications and sending them to backend
    specs = json.dumps(
        {
            "group": config.GROUP,
            "name": config.NAME,
            **{str(tracker): tracker.specs for tracker in trackers},
        }
    )
    await sendall(specs)

    while True:
        response = json.dumps(
            {
                "group": config.GROUP,
                "name": config.NAME,
                "time": round(time.time()),
                **{str(tracker): tracker.track() for tracker in trackers},
            }
        )
        try:
            await sendall(response)
        except ConnectionResetError:
            await reconnect()
        await aio.sleep(Query()["interval"])


async def reading_queries():
    while True:
        if qry_str := await recvall() == config.BACKEND_DISCONNECT_CODE:
            await reconnect()
        Query().update(qry_str)


async def main():
    # connection to backend
    global reader, writer
    reader, writer = await aio.open_connection(
        host=config.HOST_BACKEND, port=config.PORT_BACKEND
    )

    # initializing singleton Query()
    query = Query()

    # logging
    logging.basicConfig(
        filename=query.logfile,
        level=query.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    await aio.create_task(writing_responses())
    await aio.create_task(reading_queries())


if __name__ == "__main__":
    aio.run(main())

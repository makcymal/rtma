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
rw_lock = aio.Lock()
query_lock = aio.Lock()
run_lock = aio.Lock()
specs: str


async def reconnect():
    global reader, writer
    async with rw_lock:
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
        return config.BACKEND_DISCONNECT_CODE
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


async def send_responses():
    global specs
    query = Query()
    # initializing trackers
    trackers = all_trackers()

    id = f"{config.BATCH}!{config.LABEL}"

    # getting specifications and sending them to backend
    specs = json.dumps(
        {
            "header": f"spec!{id}",
            **{str(tracker): tracker.specs for tracker in trackers},
        }
    )
    await sendall(specs)

    prev_resp_hash = 0
    while True:
        async with run_lock:
            async with query_lock:
                response = json.dumps(
                    {
                        "header": f"resp!{id}!{query['mark']}!{round(time.time())}",
                        **{str(tracker): tracker.track() for tracker in trackers},
                    }
                )
                try:
                    if (curr_resp_hash := hash(response)) != prev_resp_hash:
                        await sendall(response)
                    prev_resp_hash = curr_resp_hash
                except ConnectionResetError:
                    await reconnect()
        await aio.sleep(Query()["interval"])


async def recv_queries():
    while True:
        logger.debug("Enter reading query loop")
        try:
            if (qry_str := await recvall()) == config.BACKEND_DISCONNECT_CODE:
                logger.debug("Received BACKEND_DISCONNECT_CODE, trying to reconnect")
                await reconnect()
            if qry_str == "stop":
                logger.debug("Got stop message, waiting for run_lock to acquire")
                await run_lock.acquire()
                logger.debug("run_lock acquired")
            else:
                if run_lock.locked():
                    run_lock.release()
                    logger.debug("Releasing run_lock")
                logger.debug(f"New query: {qry_str}")
                async with query_lock:
                    Query().update(qry_str)
        except ConnectionResetError:
            logger.debug("WTF it's disconnected")
            await reconnect()


async def main():
    # connection to backend
    global reader, writer
    writer = None
    while (
        not writer
        or isinstance(writer, aio.StreamWriter)
        and writer.is_closing()
        and config.ALWAYS_RECONNECT
    ):
        try:
            reader, writer = await aio.open_connection(
                host=config.HOST_BACKEND,
                port=config.PORT_BACKEND,
            )
        except OSError:
            await aio.sleep(config.RECONNECT_DELAY)

    print(f"Connected {writer.get_extra_info('peername')}")

    # initializing singleton Query()
    query = Query()

    # logging
    logging.basicConfig(
        filename=query.logfile,
        level=query.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    sending_responses = aio.create_task(send_responses())
    aio.create_task(recv_queries())
    await sending_responses


if __name__ == "__main__":
    aio.run(main())

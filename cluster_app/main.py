import os
import time
import json
import socket
import logging

from query import Query
from trackers import CpuTracker, NetTracker, MemTracker, DskTracker
import config


logger = logging.getLogger(__name__)


def broker_connection() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((config.HOST_BROKER, config.PORT_BROKER_REM))
    sock.setblocking(False)
    logger.info(
        f"Connected to broker: sockname: {sock.getsockname()}, peername: {sock.getpeername()}"
    )
    return sock


def main():
    query = Query()

    for tmpfile in ("cpu.json", "net.json", "mem.json", "dsk.json", "sensor.log"):
        if os.path.exists(tmpfile):
            os.remove(tmpfile)

    logging.basicConfig(
        filename=query.logfile,
        level=query.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    cpu_tracker = CpuTracker()
    net_tracker = NetTracker()
    mem_tracker = MemTracker()
    dsk_tracker = DskTracker()
    query.notify_subs()

    specs_dict = {
        "group": config.GROUP,
        "host": config.HOST,
        "cpu": cpu_tracker.specs,
        "net": net_tracker.specs,
        "mem": mem_tracker.specs,
        "dsk": dsk_tracker.specs,
    }
    specs = json.dumps(specs_dict).encode("utf-8")

    sock = broker_connection()
    sock.sendall(specs)

    while True:
        response_dict = {
            "group": config.GROUP,
            "host": config.HOST,
            "time": round(time.time()),
            "cpu": cpu_tracker.track(),
            "net": net_tracker.track(),
            "mem": mem_tracker.track(),
            "dsk": dsk_tracker.track(),
        }
        response = json.dumps(response_dict).encode("utf-8")

        try:
            query.update(sock.recv(1024).decode("utf-8"))
            sock.sendall(response)
        except BlockingIOError:
            pass
        except ConnectionError:
            logger.warning("Connection to broker was suddenly closed")
            sock.close()
            if config.ALWAYS_RECONNECT:
                logger.warning("Trying to reconnect")
                while sock.fileno == -1:
                    sock = broker_connection()
            else:
                logger.critical("ALWAYS_RECONNECT == False, graceful shutdown")
                exit(1)

        time.sleep(1)


main()

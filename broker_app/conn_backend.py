import socket
import logging


logger = logging.getLogger(__name__)

PORT_BACKEND_LOC = 42401
PORT_BACKEND_REM = 42402


def backend_listener() -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(("", PORT_BACKEND_LOC))
    sock.listen(1)
    logger.info(f"Listening to backend, port: {PORT_BACKEND_LOC}")
    return sock

#!python

import socket

import logging

logger = logging.getLogger(__name__)

HOST_BROKER = "localhost"  # subject to change
PORT_BROKER_LOC = 42400
PORT_BROKER_REM = 42400


def broker_connection() -> socket.socket:
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((HOST_BROKER, PORT_BROKER_REM))
    logger.info(
        f"Connected to broker: sockname: {conn.getsockname()}, peername: {conn.getpeername()}"
    )
    return conn

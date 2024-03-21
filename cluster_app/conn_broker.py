#!python

import socket


import logging

logger = logging.getLogger(__name__)


HOST_BROKER = "localhost"   # subject to change
PORT_BROKER_LOC = 42400
PORT_BROKER_REM = 42400


conn_backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_backend.connect((HOST_BROKER, PORT_BROKER_REM))
logger.info("Connected to broker")

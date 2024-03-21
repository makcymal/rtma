#!python

import socket


HOST_BROKER = "localhost"
PORT_BROKER_LOC = 42402
PORT_BROKER_REM = 42401


conn_backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_backend.connect((HOST_BROKER, PORT_BROKER_REM))

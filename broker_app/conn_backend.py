#!python

import socket


PORT_BACKEND_LOC = 42401
PORT_BACKEND_REM = 42402


conn_backend = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_backend.bind(("", PORT_BACKEND_LOC))
conn_backend.listen(1)

#!python

import socket


PORT_BACKEND_LOC = 42403
PORT_BACKEND_REM = 42404


conn_cluster = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_cluster.bind(("", PORT_BACKEND_LOC))
conn_cluster.listen(1)

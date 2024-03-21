#!python

import socket


PORT_CLUSTER_LOC = 42400
PORT_CLUSTER_REM = 42400


conn_cluster = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_cluster.bind(("", PORT_CLUSTER_LOC))
conn_cluster.listen(1024)

import os
import socket
import logging


logger = logging.getLogger(__name__)

HOST = socket.gethostname() if os.environ.get("RTMA_BROKER") is not None else ""
PORT_CLUSTER_LOC = 42400
PORT_CLUSTER_REM = 42400

with open("/proc/sys/net/core/somaxconn", "r") as somaxconn_file:
    SOMAXCONN = int(somaxconn_file.read())
    
MAXCONN = min(SOMAXCONN, 200)
logger.info(f"SOMAXCONN is {SOMAXCONN}")
logger.info(
    f"Actually broker will listen up to min(SOMAXCONN, 200) = {MAXCONN} connections"
)


def cluster_listener() -> socket.socket:
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((HOST, PORT_CLUSTER_LOC))
    serv.listen(MAXCONN)
    logger.info(f"Listening to cluster, port: {PORT_CLUSTER_LOC}")
    return serv

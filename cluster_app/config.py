import socket
import secrets
import random

DEBUG = False
HOST_BACKEND = "147.45.49.111"
PORT_BACKEND = 42400
# нельзя использовать !? в названии
BATCH = "gvr:knl"
LABEL = socket.gethostname() + str(random.randint(1, 500))
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 3
BACKEND_DISCONNECT_CODE = f"{secrets.randbits(32)}"

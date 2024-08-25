import socket
import secrets
import random

DEBUG = False
HOST_BACKEND = "localhost"
PORT_BACKEND = 42400
# нельзя использовать !? в названии
BATCH = "gvr:knl"
LABEL = "komp"+ str(random.randint(1, 50))
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 3
BACKEND_DISCONNECT_CODE = f"{secrets.randbits(32)}"

import socket
import secrets


HOST_BACKEND = "localhost"
PORT_BACKEND = 42400
GROUP = "gvr:knl"
NAME = socket.gethostname()
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 10
BACKEND_DISCONNECT_CODE = f"{secrets.randbits(32)}"

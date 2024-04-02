import socket
import secrets


HOST_BACKEND = "localhost"
PORT_BACKEND = 42400
# нельзя использовать !? в названии
BATCH = "gvr:knl"
LABEL = socket.gethostname()
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 10
BACKEND_DISCONNECT_CODE = f"{secrets.randbits(32)}"

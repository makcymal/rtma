import socket
import secrets


HOST_BACKEND = "159.93.32.219"
PORT_BACKEND = 42400
# нельзя использовать !? в названии
BATCH = "gvr:knl"
LABEL = socket.gethostname()
ALWAYS_RECONNECT = True
RECONNECT_DELAY = 3
BACKEND_DISCONNECT_CODE = f"{secrets.randbits(32)}"

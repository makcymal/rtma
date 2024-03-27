import socket
import selectors
import logging

import conn_cluster
import conn_backend


logger = logging.getLogger(__name__)
    
    
def main():
    serv_cluster = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_backend = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    selector = selectors.DefaultSelector()
    
    d = {selector: 1}

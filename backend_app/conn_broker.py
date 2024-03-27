import json
import time
import socket
import logging
import asyncio

from fastapi import WebSocket


logger = logging.getLogger(__name__)


INTERVAL = 1
SOCKET_PATH = '/var/run/rtma/backend-broker-socket'


class ConnManager:
    
    __slots__ = ("_clients", "_queries", "_queries_counter", "_responses", "_expires", "_lock")
    
    def __init__(self):
        self._clients = {}
        self._queries = set()
        self._queries_counter = {}
        self._responses = {}
        self._expires = 0
                
        self._lock = asyncio.Lock()
        
        self._sock_broker = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            self._sock_broker.connect(SOCKET_PATH)
            logger.info(f"Broker connected on socket path {SOCKET_PATH}")
        except ConnectionRefusedError:
            logger.critical(f"Cannot connect to broker, graceful shutdown")
            exit(1)
        
        logger.debug(f"Created empty {self.__class__.__name__}")
    
    def _add_query(self, ws: WebSocket, query: str):
        self._clients[ws] = query
        self._queries.add(query)
        if query not in self._queries_counter:
            self._queries_counter[query] = 0
            logger.debug(f"Query {query} added")
        self._queries_counter[query] += 1
        logger.debug(f"Query {query} counter increased: {self._queries_counter[query]}")
        
    def _remove_query(self, ws: WebSocket):
        old_query = self._clients[ws]
        self._queries_counter[old_query] -= 1
        logger.debug(f"Query {old_query} decreased: {self._queries_counter[old_query]}")
        if self._queries_counter[old_query] == 0:
            self._queries.remove(old_query)
            logger.debug(f"Query {old_query} removed")
      
    async def register(self, ws: WebSocket, query: str):
        await ws.accept()
        async with self._lock:
            self._add_query(ws, query)
        
    async def update(self, ws: WebSocket, query: str):
        async with self._lock:
            self._remove_query(ws)
            self._add_query(ws, query) 

    async def unregister(self, ws: WebSocket):
        async with self._lock:
            self._remove_query(ws)
            del self._clients[ws]        

    async def _query_broker(self):
        queries = list(self._queries)
        self._sock_broker.sendall(json.dumps(queries).encode("utf-8"))


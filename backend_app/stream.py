import json
import logging
import asyncio
import socket
from fastapi import WebSocket


logger = logging.getLogger(__name__)

BROKER_HOST = "127.0.0.1"
BROKER_PORT = 42401
broker_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
broker_conn.connect((BROKER_HOST, BROKER_PORT))


class QueryManager:

    __slots__ = ("queries", "sockets", "_query_map", "_query_counter")

    def __init__(self):
        self.queries = set()
        self.sockets = set()
        self._query_map = {}
        self._query_counter = {}
        logger.debug(f"Created empty {self.__class__.__name__}")

    def _add_query(self, ws: WebSocket, query: str):
        # стандартный майкрософтовский энвелоуп
        self._query_map[ws] = query
        self.queries.add(query)
        if query not in self._query_counter:
            self._query_counter[query] = 0
            logger.debug(f"Query {query} added")
        self._query_counter[query] += 1
        logger.debug(f"Query {query} counter increased: {self._query_counter[query]}")

    def _remove_query(self, ws: WebSocket):
        if ws not in self._query_map:
            return

        old_query = self._query_map[ws]
        self._query_counter[old_query] -= 1
        logger.debug(f"Query {old_query} decreased: {self._query_counter[old_query]}")
        if self._query_counter[old_query] == 0:
            self.queries.remove(old_query)
            logger.debug(f"Query {old_query} removed")

    async def register(self, ws: WebSocket, query: str):
        if ws not in self.sockets:
            await ws.accept()
            self.sockets.add(ws)
        
        # индиана джонс
        self._remove_query(ws)
        self._add_query(ws, query)
        
        dump = json.dumps(list(self.queries))
        await broker_conn.sendall(dump)

    def unregister(self, ws: WebSocket):
        self.sockets.remove(ws)
        self._remove_query(ws)
        del self._query_map[ws]


class ResponsesManager:
    def __init__(self) -> None:
        pass


query_mgr = QueryManager()
responses_mgr = ResponsesManager()

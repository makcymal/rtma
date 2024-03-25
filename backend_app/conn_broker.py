import time


INTERVAL = 1


class QueryManager:
    def __init__(self):
        self._responses = {}

    async def _call_broker(self, query: str): ...

    async def __getitem__(self, query: str) -> bytes:
        if query in self._responses:
            resp = self._responses[query]
            if time.time() > resp["expires"]:
                resp["data"] = await self._call_broker(query)
                resp["expires"] = time.time() + INTERVAL
        else:
            data = await self._call_broker(query)
            self._responses[query] = {
                "data": data,
                "expires": time.time() + INTERVAL,
            }
        return self._responses[query]

import os
import json
import logging
from copy import deepcopy as cp
from utils import Publisher, Singleton


logger = logging.getLogger(__name__)


class Query(Publisher, metaclass=Singleton):

    __slots__ = (
        "_qry",
        "_default_qry",
        "_subs",
        "qryfile",
        "logfile",
        "loglevel",
        "debug",
    )

    def __init__(self):
        super().__init__()

        self.qryfile = os.path.join(os.path.dirname(__file__), "query.fallback.json")

        if os.environ.get("RTMA_SENSOR") is not None:
            self.logfile = "/var/log/rtma/rtma-sensor.log"
            self.debug = False
            self.loglevel = logging.INFO
        else:
            self.logfile = "sensor.log"
            self.debug = True
            self.loglevel = logging.DEBUG

        with open(self.qryfile, "r") as qryfile:
            self._default_qry = json.load(qryfile)
            self._qry = cp(self._default_qry)

        logger.info(f"Query initialized with debug = {self.debug}")

    def update(self, qry_str: str):
        self._qry = json.loads(qry_str)
        logger.info("Updating query: ok")
        self.notify_subs()

    def __getitem__(self, key: str):
        try:
            return self._qry[key]
        except Exception as err:
            logger.error(f"Invalid order: unknown {str(err)} key")
            logger.warning("Default order will be used")
            self._qry = cp(self._default_qry)

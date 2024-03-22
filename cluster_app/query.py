import os
import json
import logging
from copy import deepcopy as cp
from utils import Publisher, Singleton


logger = logging.getLogger(__name__)


class Query(Publisher, metaclass=Singleton):

    __slots__ = (
        "_que",
        "_default_que",
        "_subs",
        "quefile",
        "logfile",
        "loglevel",
        "debug",
    )

    def __init__(self):
        super().__init__()

        self.quefile = os.path.join(os.path.dirname(__file__), "query.json")

        if int(os.getenv("RTMA_SENSOR", "0")) == 1:
            self.logfile = "/var/log/rtma-sensor/sensor.log"
            self.debug = False
            self.loglevel = logging.INFO
        else:
            self.logfile = "sensor.log"
            self.debug = True
            self.loglevel = logging.DEBUG

        with open(self.quefile, "r") as quefile:
            self._default_que = json.load(quefile)
            self._que = cp(self._default_que)

        logger.info(f"Query initialized with debug = {self.debug}")

    def update(self, que_str: str):
        self._que = json.loads(que_str)
        logger.info("Updating query: ok")
        self.notify_subs()

    def __getitem__(self, key: str):
        try:
            return self._que[key]
        except Exception as err:
            logger.error(f"Invalid order: unknown {str(err)} key")
            logger.warning("Default order will be used")
            self._que = cp(self._default_que)

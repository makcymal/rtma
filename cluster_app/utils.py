import typing as tp
import logging
from threading import Lock
from abc import abstractmethod, ABC


logger = logging.getLogger(__name__)


class Subscriber(ABC):

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_update(self):
        pass


class Publisher:

    _subs: tp.Set[Subscriber]

    def __init__(self):
        self._subs = set()

    def subscribe(self, sub: Subscriber):
        self._subs.add(sub)
        logger.debug(f"{str(sub)} subscribed")

    def unsubscribers(self, sub: Subscriber):
        self._subs.remove(sub)
        logger.debug(f"{str(sub)} unsubscribed")

    def notify_subs(self):
        for sub in self._subs:
            sub.get_update()
        logger.debug("Notifying subscribers: ok")


class Singleton(type):

    _instance = None
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if not cls._instance:
                instance = super().__call__(*args, **kwargs)
                cls._instance = instance

                logger.debug(f"Singleton {cls} accessed for the first time")

        return cls._instance

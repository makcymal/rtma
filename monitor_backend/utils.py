from threading import Lock
import typing as tp
from abc import abstractmethod, ABC
import logging

logger = logging.getLogger(__name__)


class Subscriber(ABC):
    
    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def get_notification(self):
        pass


class Publisher:

    subs: tp.Set[Subscriber]

    def __init__(self):
        self.subs = set()

    def subscribe(self, sub: Subscriber):
        self.subs.add(sub)
        logger.debug(f"{str(sub)} subscribed")

    def unsubscribers(self, sub: Subscriber):
        self.subs.remove(sub)
        logger.debug(f"{str(sub)} unsubscribed")

    def notify_subs(self):
        for sub in self.subs:
            sub.get_notification()
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

#!python

import os
import sys
import psutil as ps
import json
import typing as tp
from utils import Publisher, Subscriber, Singleton
from abc import abstractmethod, ABC

import logging

logger = logging.getLogger(__name__)


class Config(Publisher, metaclass=Singleton):

    __slots__ = ("_cfg", "subs", "debug")

    def __init__(self):
        super().__init__()
        filename = (
            "/etc/rtma/config.json" if os.getenv("RTMA_SENSOR") else "config.json"
        )
        logger.debug(f"Reading config from {filename}")
        try:
            with open(filename) as cfg_file:
                self._cfg = json.load(cfg_file)
                logger.debug("Reading config: ok")

        except Exception as err:
            logger.error(str(err))

    def update(self, cfg_str: str):
        self._cfg = json.loads(cfg_str)
        logger.debug("Updating config: ok")
        self.notify_subs()

    def __getitem__(self, key: str):
        try:
            return self._cfg[key]
        except Exception as err:
            logger.error(str(err))
            logger.warning("Default config will be used")

            try:
                with open("config.default.json") as cfg_file:
                    self._cfg = json.load(cfg_file)
                    self.notify_subs()
            except Exception as err:
                logger.critical(str(err))
                exit(-1)


class Tracker(Subscriber, ABC):

    def __init__(self):
        Config().subscribe(self)

    def get_notification(self):
        self.load_config()

    @abstractmethod
    def load_config(self):
        pass

    @abstractmethod
    def track(self):
        pass


class CpuTracker(Tracker):

    __slots__ = ("fields", "interval")

    fields: tp.List[str]
    interval: float

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "CpuTracker"

    def load_config(self):
        cfg = Config()
        self.fields = cfg["cpu_fields"]
        self.interval = cfg["interval"]
        logger.debug(f"{str(self)} load new config: ok")

    def track(self) -> dict:
        """Time spent by CPU on sys, user, ... tasks or being idle"""

        raw_cpu_times = ps.cpu_times_percent(self.interval)

        try:
            cpu_times = {field: getattr(raw_cpu_times, field) for field in self.fields}
        except AttributeError as err:
            logger.warning(str(err))
            logger.debug(f"Invalid fields in config for {str(self)}, using all")
            self.fields = raw_cpu_times._stats
            cpu_times = {field: getattr(raw_cpu_times, field) for field in self.fields}

        with open("sensor.json", "a") as file:
            json.dump(cpu_times, file, indent=4)

        return cpu_times


class NetTracker(Tracker):

    __slots__ = ("conn_fields", "stat_fields", "stat_values")

    conn_fields: tp.List[str]
    conn_statuses: tp.Set[str]
    stat_fields: tp.List[str]
    prev_stat_values: tp.List[dict]

    def __init__(self):
        super().__init__()

    def __str__(self):
        return "NetTracker"

    def load_config(self):
        cfg = Config()
        self.conn_fields = cfg["net_conn_fields"]
        self.conn_statuses = set(cfg["net_conn_statuses"])
        self.io_fields = cfg["net_io_fields"]
        logger.debug(f"{str(self)} load new config: ok")

    def track(self) -> tp.List[dict]:
        raw_net_conn = ps.net_connections("tcp")
        if not raw_net_conn:
            return []

        try:
            net_conn = [
                {field: getattr(conn, field) for field in self.fields}
                for conn in raw_net_conn
                if conn.status in self.conn_statuses
            ]
        except AttributeError as err:
            logger.warning(str(err))
            logger.debug(f"Invalid fields in config for {str(self)}, using all")
            self.fields = raw_net_conn._stats
            net_conn = [
                {field: getattr(conn, field) for field in self.fields}
                for conn in raw_net_conn
                if conn.status in self.conn_statuses
            ]

        with open("sensor.json", "a") as file:
            json.dump(net_conn, file, indent=4)

        return net_conn


def main():
    for file in ("sensor.json", "sensor.log"):
        if os.path.exists(file):
            os.remove(file)

    logging.basicConfig(
        filename="sensor.log",
        level=logging.DEBUG,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    cpu_tracker = CpuTracker()
    net_tracker = NetTracker()
    Config().notify_subs()

    # cpu = cpu_tracker.track()
    # print(cpu)
    # net = net_tracker.track()
    # print(net)


main()

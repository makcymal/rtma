#!python

from abc import abstractmethod, ABC
import json
import psutil as ps
from copy import deepcopy as cp
from collections import namedtuple

from utils import Subscriber, Pair
from query import Query

import logging

logger = logging.getLogger(__name__)


class Tracker(Subscriber, ABC):

    __slots__ = ("debug", "specs", "interval", "extended", "fields", "prev")

    def __init__(self):
        Query().subscribe(self)
        self._fill_specs()
        logger.info(f"Got {str(self)} specs")

    def get_update(self):
        query = Query()
        self.debug = query.debug
        self.interval = query["interval"]
        self.extended = query[f"{str(self)}_extended"]
        self.fields = set(query[f"{str(self)}_fields"])
        self._validate_query_fields()
        logger.info(f"{str(self)}_tracker updated query")

    @abstractmethod
    def _fill_specs(self):
        pass

    @abstractmethod
    def _validate_query_fields(self):
        pass

    @abstractmethod
    def track(self) -> dict | list[dict]:
        pass


class CpuTracker(Tracker):

    VALID_FIELDS = set(
        (
            "system",
            "user",
            "nice",
            "idle",
            "iowait",
            "irq",
            "softirq",
            "steal",
            "guest",
            "guest_nice",
            "freq",
        )
    )

    def __str__(self) -> str:
        return "cpu"

    def _fill_specs(self):
        self.specs["cores_phys"] = ps.cpu_count(logical=False)
        self.specs["cores_logic"] = ps.cpu_count(logical=True)

        cpu_freq = ps.cpu_freq(percpu=True)
        self.specs["min_freq"] = [core.min for core in cpu_freq]
        self.specs["max_freq"] = [core.max for core in cpu_freq]

    def _validate_query_fields(self):
        invalid_fields = self.fields.difference(self.__class__.VALID_FIELDS)
        if invalid_fields:
            logger.warning(
                f"Got invalid fields in query for CpuTracker: {list(invalid_fields)}, they will be ignored"
            )
            self.fields.difference_update(invalid_fields)

    def _get_response(self) -> dict:
        response = {}

        cpu_times = ps.cpu_times_percent(percpu=False)
        cpu_times_fields = self.fields.intersection(cpu_times._fields)
        response = {field: getattr(cpu_times, field) for field in cpu_times_fields}
        logger.debug(
            "Filled cpu_tracker.response with cpu_times_percent for the entire cpu"
        )

        if "freq" in self.fields:
            cpu_freq = ps.cpu_freq(percpu=False)
            response["freq"] = cpu_freq.current
            logger.debug("Filled cpu_tracker.response with cpu_freq for the entire cpu")

        return response

    def _get_response_percpu(self) -> list[dict]:
        response = []

        cpu_times_percpu = ps.cpu_times_percent(percpu=True)
        if cpu_times_percpu:
            cpu_times_fields = self.fields.intersection(cpu_times_percpu[0]._fields)
            response = [
                {field: getattr(cpu_times, field) for field in cpu_times_fields}
                for cpu_times in cpu_times_percpu
            ]
            logger.debug(
                "Filled cpu_tracker.response with cpu_times_percent per each cpu"
            )
        else:
            logger.error(
                "Cannot get psutil.cpu_times_percent(percpu=True): got empty list"
            )

        if "freq" in self.fields:
            cpu_freq_percpu = ps.cpu_freq(percpu=True)
            for core_response, freq in zip(response, cpu_freq_percpu):
                core_response["freq"] = freq
            logger.debug("Filled cpu_tracker.response with cpu_freq per each cpu")

        return response

    def track(self) -> dict | list[dict]:
        response = (
            self._get_response_percpu() if self.extended else self._get_response()
        )

        if self.debug:
            with open("sensor.json", "a") as file:
                json.dump(response, file, indent=4)

        return response


class NetTracker(Tracker):
    """
    response scheme:
    {
        "bytes": (in, out),
        "packets": (in, out),
        "errors": (in, out),
        "drops": (in, out),
    }

    extended response scheme:
    {
        "lo": {
            "bytes": (in, out),
            "packets": (in, out),
            "errors": (in, out),
            "drops": (in, out),
        },
        "eth0": {
            "bytes": (in, out),
            "packets": (in, out),
            "errors": (in, out),
            "drops": (in, out),
        },
    }
    """

    FIELDS_MAP = {
        "bytes": ("bytes_recv", "bytes_sent"),
        "packets": ("packets_recv", "packets_sent"),
        "errors": ("errin", "errout"),
        "drops": ("dropin", "dropout"),
    }
    VALID_FIELDS = set(FIELDS_MAP.keys())

    def __str__(self):
        return "net"

    def _fill_specs(self):
        self.specs = {}
        self.specs["nics"] = list(ps.net_io_counters(pernic=True).keys())

    def _validate_query_fields(self):
        invalid_fields = self.fields.difference(self.__class__.VALID_FIELDS)
        if invalid_fields:
            self.fields.difference_update(invalid_fields)
            logger.warning(
                f"Got invalid fields in query for NetTracker: {list(invalid_fields)}, they will be ignored"
            )

    def _get_io_without_prev(self, io: namedtuple) -> dict:
        return {
            field: (
                io._asdict()[self.__class__.FIELDS_MAP[field][0]] / self.interval,
                io._asdict()[self.__class__.FIELDS_MAP[field][1]] / self.interval,
            )
            for field in self.fields
        }

    def _get_io_with_prev(self, io: namedtuple, prev: namedtuple) -> dict:
        return {
            field: (
                (
                    io._asdict()[self.__class__.FIELDS_MAP[field][0]]
                    - prev._asdict()[self.__class__.FIELDS_MAP[field][0]]
                )
                / self.interval,
                (
                    io._asdict()[self.__class__.FIELDS_MAP[field][1]]
                    - prev._asdict()[self.__class__.FIELDS_MAP[field][1]]
                )
                / self.interval,
            )
            for field in self.fields
        }

    def _get_response(self) -> dict:
        prev = self.specs["prev"]
        net_io = ps.net_io_counters(pernic=False)
        response = (
            self._get_io_with_prev(net_io, prev)
            if prev
            else self._get_io_without_prev(net_io)
        )
        self.specs["prev"] = net_io
        return response

    def _get_response_pernic(self) -> dict:
        prev = self.specs["prev"]
        net_io_pernic = ps.net_io_counters(pernic=True)
        response = (
            {
                nic: self._get_io_with_prev(net_io, prev[nic])
                for nic, net_io in net_io_pernic.items()
            }
            if prev
            else {
                nic: self._get_io_without_prev(net_io)
                for nic, net_io in net_io_pernic.items()
            }
        )
        self.specs["prev"] = net_io_pernic
        return response

    def track(self) -> dict:
        empty_response = bool(self.specs["prev"])

        if self.extended:
            response = self._get_response_pernic()
        else:
            response = self._get_response()

        return {} if empty_response else response


class MemTracker(Tracker):

    def __str__(self):
        return "mem"

    def _fill_specs(self):
        self.specs["mem_total"] = ps.virtual_memory().total
        self.specs["swp_total"] = ps.swap_memory().total


class DskTracker(Tracker):

    def __str__(self):
        return "dsk"

    def _fill_specs(self):
        partitions = ps.disk_partitions()
        self.specs["devices"] = [
            {
                "name": part.device,
                "mountpoint": part.mountpoint,
                "total": ps.disk_usage(part.mountpoint).total,
            }
            for part in partitions
        ]


query = Query()
net_tracker = NetTracker()
query.notify_subs()


print(net_tracker.track())
print(net_tracker.track())

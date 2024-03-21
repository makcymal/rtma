#!python

from query import Query
from trackers import CpuTracker, NetTracker, MemTracker, DskTracker


import logging

logger = logging.getLogger(__name__)


def main():
    query = Query()

    logging.basicConfig(
        filename=query.logpath,
        level=query.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    hardware_specs = HardwareSpecs()

    cpu_tracker = CpuTracker()
    # net_tracker = NetTracker()
    # mem_tracker = MemTracker()
    # dsk_tracker = DskTracker()
    query.notify_subs()

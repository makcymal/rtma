#!python

import time
import json
from query import Query
from trackers import CpuTracker, NetTracker, MemTracker, DskTracker


import logging

logger = logging.getLogger(__name__)


def main():
    query = Query()

    logging.basicConfig(
        filename=query.logfile,
        level=query.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )

    cpu_tracker = CpuTracker()
    net_tracker = NetTracker()
    mem_tracker = MemTracker()
    dsk_tracker = DskTracker()
    query.notify_subs()
    
    for i in range(2):
        cpu_response = cpu_tracker.track()
        net_response = net_tracker.track()
        mem_response = mem_tracker.track()
        dsk_response = dsk_tracker.track()
        response = {
            "cpu": cpu_response,
            "net": net_response,
            "mem": mem_response,
            "dsk": dsk_response,
        }
        with open("response.json", "w") as response_json:
            json.dump(response, response_json)
        time.sleep(1)
        
main()

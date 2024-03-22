import os
import socket
import time
import json
import logging

from query import Query
from trackers import CpuTracker, NetTracker, MemTracker, DskTracker
import conn_broker


logger = logging.getLogger(__name__)


def main():
    query = Query()

    for tmpfile in ("cpu.json", "net.json", "mem.json", "dsk.json", "sensor.log"):
        if os.path.exists(tmpfile):
            os.remove(tmpfile)

    logging.basicConfig(
        filename=query.logfile,
        level=query.loglevel,
        format="%(levelname)s:%(asctime)s - %(module)s:%(lineno)s - %(message)s",
        datefmt="%H:%M:%S",
    )
    
    host = socket.gethostname()

    cpu_tracker = CpuTracker()
    net_tracker = NetTracker()
    mem_tracker = MemTracker()
    dsk_tracker = DskTracker()
    query.notify_subs()
    
    broker_conn = conn_broker.broker_connection()
    
    specs_dict = {
        "host": host,
        "cpu": cpu_tracker.specs,
        "net": net_tracker.specs,
        "mem": mem_tracker.specs,
        "dsk": dsk_tracker.specs,
    }
    
    with open("specs.json", "w") as specs_json:
        json.dump(specs_dict, specs_json)
    specs = json.dumps(specs_dict).encode("utf-8")
    
    broker_conn.sendall(specs)

    while True:
        response_dict = {
            "host": host,
            "time": round(time.time()),
            "cpu": cpu_tracker.track(),
            "net": net_tracker.track(),
            "mem": mem_tracker.track(),
            "dsk": dsk_tracker.track(),
        }
        
        with open("response.json", "w") as response_json:
            json.dump(response_dict, response_json, indent=4)
        response = json.dumps(response_dict).encode("utf-8")

        broker_conn.sendall(response)
        
        time.sleep(1)

main()

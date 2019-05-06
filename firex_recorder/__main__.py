import sys
import time

import argparse
from json import dumps

from celery import Celery
from celery.events import EventReceiver
from threading import Timer

TERMINAL_EVENT_TYPES = ['task-succeeded', 'task-failed', 'task-revoked']


class Recoder:
    def __init__(self, broker, destination):
        self.celery_app = Celery(broker=broker)
        self.destination = destination
        self.root_uuid = None
        self.root_completed = False

    def record(self):
        print("Beginning to record")
        # Loop to receive the events from celery.
        try_interval = 1
        while True:
            try:
                try_interval *= 2  # exponential timeout
                with self.celery_app.connection() as conn:
                    conn.ensure_connection(max_retries=1, interval_start=0)
                    receiver = EventReceiver(conn,
                                             handlers={"*": self.record_event},
                                             app=self.celery_app)
                    try_interval = 1
                    receiver.capture(limit=None, timeout=None, wakeup=True)
            except SystemExit:
                raise
            except Exception as e:
                if self.root_completed:
                    return

                print(e)
                if try_interval > 32:
                    # by now we've already waited 63 seconds. Assume broker is shutdown.
                    # We should do the same
                    return
                time.sleep(try_interval)

    def record_event(self, event):
        with open(self.destination, "a") as rec:
                    event_line = dumps(event)
                    rec.write(event_line + "\n")

        try:
            if not self.root_uuid:
                self.root_uuid = event["uuid"]
            else:
                if event["uuid"] == self.root_uuid and event["type"] in TERMINAL_EVENT_TYPES:
                    print("Root task has completed")
                    self.root_completed = True
        except KeyError:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--destination',
        help='A destination file to contain the recording of celery events')
    parser.add_argument(
        "--broker",
        help="the broker url")
    parser.add_argument('--timeout', help='Maximum lifetime of this service, in seconds', type=int,
                        default=60*60*24*2)
    args = parser.parse_args()

    rec = Recoder(args.broker, args.destination)
    t = Timer(args.timeout, lambda: sys.exit(0))
    try:
        rec.record()
        t.cancel()
    finally:
        print("Shutting down recording")

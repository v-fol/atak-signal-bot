import os
import signal
import subprocess
import time
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from config import SCRIPT_TO_RUN

logging.basicConfig(level=logging.INFO)

DIRECTORY_TO_WATCH = os.path.dirname(os.path.abspath(SCRIPT_TO_RUN))


class ScriptReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_script()

    def start_script(self):
        logging.info(f"Starting script: {SCRIPT_TO_RUN}")
        self.process = subprocess.Popen(["python", SCRIPT_TO_RUN])

    def restart_script(self):
        logging.info(f"Restarting script: {SCRIPT_TO_RUN}")
        self.process.send_signal(signal.SIGINT)
        self.process.wait()
        self.start_script()

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            logging.info(f"Detected change in {event.src_path}")
            self.restart_script()

if __name__ == "__main__":
    logging.info(f"Watching directory: {DIRECTORY_TO_WATCH}")
    event_handler = ScriptReloader()
    observer = Observer()
    observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
    logging.info(f"Watching directory: {DIRECTORY_TO_WATCH}")
    try:
        observer.start()
        logging.info(f"Watching directory: {DIRECTORY_TO_WATCH}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

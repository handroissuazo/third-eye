import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

class Watchdog:

    def start(self):
        if "sender" == self.operational_mode:
            print("sender")
        elif "receiver" == self.operational_mode:
            print("receiver")

    def __init__(self, dir_to_watch, size_limit, option):
        self.directory_to_watch = dir_to_watch
        self.dir_size_limit = size_limit
        self.operational_mode = option

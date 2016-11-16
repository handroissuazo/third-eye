from queue import Queue


class PBuffer:

    def enqueue(self, destination, action, data=""):
        packet_to_queue = {
            "destination": destination,
            "action": action,
            "data": data
        }

        self.comm_queue.put(packet_to_queue)

    def dequeue(self):
        self.last_object_in_queue = self.comm_queue.get()
        self.comm_queue.task_done()
        return self.last_object_in_queue

    def thanks(self):
        self.last_object_in_queue = {}

    def no_thanks(self):
        if self.last_object_in_queue is not {}:
            self.comm_queue.put(self.last_object_in_queue)
            self.last_object_in_queue = {}

    def __init__(self):
        self.comm_queue = Queue()
        self.last_object_in_queue = {}

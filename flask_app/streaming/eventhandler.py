# simple class to handle events such as inbound messages -
#  to be shared across the application for sse streaming

from queue import Queue 

class EventHandler:
    def __init__(self, queue_names: list=[], queue_sizes=0):
        """
        Handler to deal with inbound quote messages, to allow distribution to 
        different SSE streams in different pages 
        (bit of an ugly hack)
        Args:
        queues: list of queue names, used to instantiate corresponding queues for sse message storage 
        queue_sizes: max_size for queues - if set to <= 0 then queue size is infinite 
        """
        self.queue_names = queue_names
        self.queue_sizes = queue_sizes 
        if len(self.queue_names):
            self.init_queues()

    def init_queues(self):
        for name in self.queue_names:
            setattr(self, name, Queue(maxsize=self.queue_sizes))

    def add(self, item, queue_name):
        if self.queue_name_check(queue_name):
            getattr(self, queue_name).put(item)
    
    def listen(self, queue_name):
        if self.queue_name_check(queue_name):
            return getattr(self, queue_name).get()

    def empty(self, queue_name):
        if self.queue_name_check(queue_name):
            return getattr(self, queue_name).qsize() == 0

    def queue_name_check(self, queue_name):
        return queue_name in self.queue_names

    def add_queue(self, queue_name):
        if not self.queue_name_check(queue_name):
            setattr(self, queue_name, Queue(maxsize=self.queue_sizes))
            self.queue_names.append(queue_name)

    def remove_queue(self, queue_name):
        if queue_name in self.queue_names:
            delattr(self, queue_name)
            self.queue_names.remove(queue_name)

    def add_all(self, item):
        for name in self.queue_names:
            getattr(self, name).put(item)
    

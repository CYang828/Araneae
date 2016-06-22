# coding:utf8


from gevent.queue import (Queue, Empty)

from Araneae.schedulers import Scheduler
from Araneae.constant import (DEFAULT_SCHEDULER_PULL_TIMEOUT,DEFAULT_SCHEDULER_PULL_COUNT)
from Araneae.man.exceptions import SchedulerEmpty

class MemoryScheduler(Scheduler):

    def __init__(self, scheduler_name):
        self._scheduler_key = 'Scheduler:{scheduler_name}'.format(scheduler_name=scheduler_name)
        self._queue = Queue()

    @classmethod
    def from_spider(cls, spider):
        scheduler_name = spider.settings.get('SPIDER_NAME')
        return cls(scheduler_name)

    def __len__(self):
        return self._queue.qsize()

    def push(self, r): 
        self._queue.put_nowait(r)

    def pull(self, count=DEFAULT_SCHEDULER_PULL_COUNT, timeout=DEFAULT_SCHEDULER_PULL_TIMEOUT):
        try:
            return self._queue.get(timeout=timeout)
        except Empty:
            raise SchedulerEmpty

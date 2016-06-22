# coding:utf8

from Araneae.utils.loader import load_object
from Araneae.constant import (DEFAULT_SCHEDULER_PULL_TIMEOUT,DEFAULT_SCHEDULER_PULL_COUNT)


class SchedulerFactory(object):
    """ 
    单机调度器,包含dupefilter
    分布式的dupefilter在master中

    """

    def __init__(self, scheduler, dupefilter):
        self._scheduler = scheduler
        self._dupefilter = dupefilter

    def __len__(self):
        return len(self._scheduler)

    def push(self, r):
        if self._dupefilter.put(r):
            self._scheduler.push(r)
            return True
        else:
            return False

    def pull(self, count=DEFAULT_SCHEDULER_PULL_COUNT, timeout=DEFAULT_SCHEDULER_PULL_TIMEOUT):
        return self._scheduler.pull(timeout)

    def clear(self):
        self._scheduler.clear()
        self._dupefilter.clear()



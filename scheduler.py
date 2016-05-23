#*-*coding:utf8*-*

from collections import deque
import gevent as GEV
import gevent.queue as GEVQ

import Araneae.db as DB
import Araneae.dupefilter as DFT
import Araneae.man.exception as EXP

DEFAULT_PULL_TIMEOUT = 5


class BaseScheduler(object):
    def pull(self):
        raise NotImplementedError('调度器需要实现pull方法')

    def push(self):
        raise NotImplementedError('调度器需要实现push方法')


class MemoryScheduler(BaseScheduler):
    def __init__(self, scheduler_name, **conf):
        self._scheduler_key = 'Scheduler:' + scheduler_name
        self._queue = GEVQ.Queue()

    def __len__(self):
        return self._queue.qsize()

    def push(self, d):
        self._queue.put_nowait(d)

    def pull(self, timeout = DEFAULT_PULL_TIMEOUT):
        try:
            return self._queue.get(timeout = timeout)
        except GEVQ.Empty:
            pass

class RedisScheduler(BaseScheduler):
    def __init__(self, scheduler_name, **redis_conf):
        self._scheduler_key = 'Scheduler:' + scheduler_name
        self._redis = DB.Redis(**redis_conf)

    def __len__(self):
        return self._redis.llen(self._scheduler_key)

    def push(self, d):
        self._redis.lpush(self._scheduler_key, d)
    
    def pull(self, timeout=5):
        data = self._redis.brpop(self._scheduler_key, timeout)

        if data:
            return data[1]
        else:
            return None

    def clear(self):
        self._redis.delete(self._scheduler_key)


class RabbitmqScheduler(BaseScheduler):
    pass


class DupeScheduler(object):
    """
    单机调度器,包含dupefilter
    分布式的dupefilter在master中

    """

    def __init__(self, scheduler, dupefilter):
        self._scheduler = scheduler
        self._dupefilter = dupefilter

    def __len__(self):
        return len(self._scheduler)

    def push(self, data):
        if self._dupefilter.put(data):
            self._scheduler.push(data)
            return True
        else:
            return False

    def pull(self, timeout = DEFAULT_PULL_TIMEOUT):
        return self._scheduler.pull(timeout)

    def clear(self):
        self._scheduler.clear()
        self._dupefilter.clear()


if __name__ == '__main__':
    redis_conf = {'host': '172.18.4.52',
                  'port': 6379,
                  'db': 8,
                  'password': None,
                  'timeout': 5,
                  'charset': 'utf8'}
    mem_scheduler = MemoryScheduler('demo')
    redis_scheduler = RedisScheduler('demo', **redis_conf)

    mem_dupefilter = DFT.MemoryDupeFilter('demo')
    redis_dupefilter = DFT.RedisDupeFilter('demo', **redis_conf)

    singleton = DupeScheduler(redis_scheduler, redis_dupefilter)
    singleton.push('aaa')
    print singleton.push('aaa')
    print singleton.pull()

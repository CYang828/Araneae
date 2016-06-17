# coding:utf8

import redis
from gevent import spawn

from Araneae.schedulers import Scheduler
from Araneae.man.exception import SchedulerEmpty
from Araneae.constant import (DEFAULT_SCHEDULER_PULL_TIMEOUT,DEFAULT_SCHEDULER_PULL_COUNT)


class RedisScheduler(Scheduler):
    """redis调度器,如果存在大量操作可以使用pipeline来节省交互时间"""

    def __init__(self, scheduler_name, redis):
        self._scheduler_key = 'Scheduler:{scheduler_name}'.format(scheduler_name=scheduler_name)
        self._redis = redis

    @classmethod
    def from_spider(self, spider):
        scheduler_name = spider.settings.get('SPIDER_NAME')
        scheduler_conf = spider.settings.getdict('SCHEDULER_CONF')
        redis = spawn(self._connect, scheduler_conf)
        return cls(scheduler_name, redis)

    def _connect(self, scheduler_conf):
        return redis.StrictRedis(**shceudler_conf)

    def __len__(self):
        return self._redis.llen(self._scheduler_key)

    def push(self, r): 
        spawn(self._push, r)
    
    def _push(self, r):
        self._scheduler.lpush(self._scheduler_key, r)

    def pull(self, count=DEFAULT_SCHEDULER_PULL_COUNT,timeout=DEFAULT_SCHEDULER_PULL_TIMEOUT):
        spawn(self._pull, count, timeout)
       
    def _pull(self, count,timeout):
        data = self._scheduler.brpop(self._scheduler_key, timeout)

        if data:
            return data[1]
        else:
            raise SchedulerEmpty

    def clear(self):
        spawn(self._clear)       

    def _clear(self):
        self._redis.delete(self._scheduler_key)


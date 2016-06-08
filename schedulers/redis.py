# coding:utf8

import redis

from Araneae.schedulers import Scheduler
from Araneae.constant import (DEFAULT_SCHEDULER_PULL_TIMEOUT,DEFAULT_SCHEDULER_PULL_COUNT)


class RedisScheduler(Scheduler):

    def __init__(self, scheduler_name, redis):
        self._scheduler_key = 'Scheduler:{scheduler_name}'.format(scheduler_name=scheduler_name)
        self._redis = redis

    @classmethod
    def from_spider(self, spider):
        scheduler_name = spider.settings.get('SPIDER_NAME')
        scheduler_conf = spider.settings.getdict('SCHEDULER_CONF')
        redis = redis.StrictRedis(**scheduler_conf)
        return cls(scheduler_name, redis)

    def __len__(self):
        return self._redis.llen(self._scheduler_key)

    def push(self, r): 
        self._scheduler.lpush(self._scheduler_key, r)

    def pull(self, count=DEFAULT_SCHEDULER_PULL_COUNT,timeout=DEFAULT_SCHEDULER_PULL_TIMEOUT):
        data = self._scheduler.brpop(self._scheduler_key, timeout)

        if data:
            return data[1]
        else:
            return None

    def clear(self):
        self._redis.delete(self._scheduler_key)


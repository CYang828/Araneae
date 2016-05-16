#*-*coding:utf8*-*
# import sys

from collections import deque

import Araneae.db as DB
from Araneae.utils.log import Plog
from Araneae.dupefilter import SingletonDupeFilter,RedisDupeFilter


class BaseScheduler(object):

    def open(self, info):
        raise NotImplementedError('调度器需要实现open方法')

    def pull(self):
        raise NotImplementedError('调度器需要实现pull方法')
    
    def push(self):
        raise NotImplementedError('调度器需要实现push方法')

class MemoryScheduler(BaseScheduler):
    
    def __init__(self,spider_name):
        self._scheduler_key = 'Scheduler:' + spider_name
        self._queue = deque([])

    def push(self,data):
        self._queue.append(data)

    def pull(self):
        return self._queue.popleft()

    def __len__(self):
        return len(self._queue)

class RedisScheduler(BaseScheduler):

    def __init__(self,spider_name,**redis_conf):
        self._scheduler_key = 'Scheduler:' + spider_name
        self._redis = DB.Redis(**redis_conf)

    def push(self, data):
        self._redis.lpush(self._scheduler_key,data)
    
    def pull(self):
        return self._redis.rpop(self._scheduler_key)

    def __len__(self):
        return self._redis.llen(self._scheduler_key)

class RabbitmqScheduler(BaseScheduler):
    pass


#单机调度器,包含dupefilter
#分布式的dupefilter在master中
class SingletonScheduler(object):
    
    def __init__(self,scheduler,dupefilter):
        self._scheduler = scheduler
        self._dupefilter = dupefilter

    def __len__(self):
        return len(self._scheduler)

    def push(self,data):
       if not self._dupefilter.exist(data):
            self._scheduler.push(data)
            return True
        else:
            return False

    def pull(self):
        return self._scheduler.pull()
    

if __name__ == '__main__':
    pass

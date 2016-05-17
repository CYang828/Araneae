#*-*coding:utf8*-*

from collections import deque

import Araneae.db as DB
import Araneae.dupefilter as DFT


class BaseScheduler(object):

    def open(self, info):
        raise NotImplementedError('调度器需要实现open方法')

    def pull(self):
        raise NotImplementedError('调度器需要实现pull方法')
    
    def push(self):
        raise NotImplementedError('调度器需要实现push方法')

class MemoryScheduler(BaseScheduler):
    
    def __init__(self,spider_name,**conf):
        self._scheduler_key = 'Scheduler:' + spider_name
        self._queue = deque([])

    def __len__(self):
        return len(self._queue)

    def push(self,data):
        self._queue.append(data)

    def pull(self):
        return self._queue.popleft()

    def clear(self):
        self._queue.clear()

class RedisScheduler(BaseScheduler):

    def __init__(self,spider_name,**redis_conf):
        self._scheduler_key = 'Scheduler:' + spider_name
        self._redis = DB.Redis(**redis_conf)

    def __len__(self):
        return self._redis.llen(self._scheduler_key)

    def push(self, data):
        self._redis.lpush(self._scheduler_key,data)
    
    def pull(self):
        return self._redis.rpop(self._scheduler_key)

    def clear(self):
        self._redis.delete(self._scheduler_key)

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
            self._dupefilter.put(data)
            return True
        else:
            return False

    def pull(self):
        return self._scheduler.pull()

    def clear(self):
        self._scheduler.clear()
        self._dupefilter.clear()
    

if __name__ == '__main__':
    redis_conf = {'host':'172.18.4.52','port':6379,'db':8,'password':None,'timeout':5,'charset':'utf8'}
    mem_scheduler = MemoryScheduler('demo')
    redis_scheduler = RedisScheduler('demo',**redis_conf)
 
    mem_dupefilter = DFT.MemoryDupeFilter('demo')
    redis_dupefilter = DFT.RedisDupeFilter('demo',**redis_conf)
 
    singleton = SingletonScheduler(redis_scheduler,redis_dupefilter)
    singleton.push('aaa')
    print singleton.push('aaa')
    print singleton.pull()

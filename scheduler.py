#*-*coding:utf8*-*

from collections import deque

class BaseScheduler(object):

    def pull(self):
        raise NotImplementedError('调度器需要实现pull方法')
    
    def push(self):
        raise NotImplementedError('调度器需要实现push方法')

    def full(self):
        raise NotImplementedError('调度器需要实现full方法')

class SingletonScheduler(BaseScheduler):
    
    def __init__(self):
        self._queue = deque([])
        self._dupefilter = set([])
       
    def push(self,data):
        self._queue.append(data)

    def pull(self):
        return self._queue.popleft()

class RedisScheduler(BaseScheduler):
    pass


class RabbitmqScheduler(BaseScheduler):
    pass



if __name__ == '__main__':
    s = SingletonScheduler()
    s.push('q')
    s.push('b')
    print s.pull()

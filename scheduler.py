#*-*coding:utf8*-*

from collections import deque

from Araneae.dupefilter import SingletonDupeFilter

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
        self._dupefilter = SingletonDupeFilter()
       
    def push(self,data):
        if not self._dupefilter.exist():
            self._queue.append(data)
            return True
        else:
            return False

    def pull(self):
        return self._queue.popleft()

    def full(self):
        pass

class RedisScheduler(BaseScheduler):
    pass


class RabbitmqScheduler(BaseScheduler):
    pass



if __name__ == '__main__':
    s = SingletonScheduler()
    s.push('q')
    s.push('b')
    print s.pull()

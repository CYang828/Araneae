#*-*coding:utf8*-*
# import sys
# sys.path.append('/home/guoweijiang')

from collections import deque
from Araneae.utils.log import Plog
from redis.exceptions import (
    ConnectionError,
    DataError,
    ExecAbortError,
    NoScriptError,
    PubSubError,
    RedisError,
    ResponseError,
    TimeoutError,
    WatchError,
)
import redis

from Araneae.dupefilter import SingletonDupeFilter


class BaseScheduler(object):

    def open(self, info):
        raise NotImplementedError('调度器需要实现open方法')

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

    def open(self, info):
        return True
       
    def push(self,data):
        if not self._dupefilter.exist(data):
            self._queue.append(data)
            return True
        else:
            return False

    def pull(self):
        return self._queue.popleft()

    def full(self):
        pass

    def __len__(self):
        return len(self._queue)

class RedisScheduler(BaseScheduler):

    __list_key_name = 'RedisListKey'

    def __init__(self):
        self.cli = None
        return

    def open(self, info):
        self.cli = redis.Redis(host = info['host'],
                               port = info['port'],
                               db = info['db'],
                               socket_timeout = info['timeout'],
                               socket_connect_timeout = info['timeout'])

        print "Connect Redis[" + info['host'] + ":" + info['port'] + "]"
        return

    def __getitem__(self, item):
        if item == 'key':
            return 'value'
        else:
            return 'None'

    def push(self, data):
        if self.cli == None:
            Plog('can not lpush due to None Redis Error')
            return False

        try:
            ret = self.cli.lpush(self.__list_key_name, data)
            print 'lpush ret = ' + str(ret)
            return True
        except(ConnectionError, TimeoutError) as e:
            print "can not lpush due to[" + str(e) + "]"
            return False

    def pull(self):
        if self.cli == None:
            Plog('can not rpop due to None Redis Error')
            return False

        try:
            ret = self.cli.rpop(self.__list_key_name)
            print 'rpop value[' + ret + ']'
            return ret
        except(ConnectionError, TimeoutError) as e:
            print "can not rpop due to[" + str(e) + "]"
            return ""

    def __len__(self):
        if self.cli == None:
            Plog('can not llen due to None Redis Error')
            return False

        try:
            ret = self.cli.llen(self.__list_key_name)
            print 'llen value[' + str(ret) + ']'
            return ret
        except(ConnectionError, TimeoutError) as e:
            print "can not llen due to[" + str(e) + "]"
            return 0

class RabbitmqScheduler(BaseScheduler):
    pass

if __name__ == '__main__':
    # s = SingletonScheduler()
    # s.push('q')
    # s.push('b')
    # print s.pull()

    sample = RedisScheduler()

    sample.open({'type':'redis',
                 'host':'10.60.0.165',
                 'port':'6379',
                 'password':'',
                 'db':0,
                 'timeout':5
                 })

    print "test __getitem_[" + sample['key'] + "], None[" + sample['abc'] + "]"

    index = 1
    while index < 10:
        sample.push(str(index))
        index += 1

    print "List Size[" + str(len(sample)) + "]"

    while len(sample) > 0:
        print "Pull a Value[" + sample.pull() + "]"



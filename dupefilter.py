#*-*coding:utf8*-*

import hashlib

class BaseDupeFilter(self):

    def exist(self,key):
        raise NotImplementedError('去重器必须实现exist方法')

    def put(self,key):
        raise NotImplementedError('去重器必须实现put方法')

    #序列化和反序列化方法

class SingletonDupeFilter(BaseDupeFilter):

    def __init__(self):
        self._set = set()

    def exist(self,key):
        key = hashlib.md5(key).hexdigest()

        return True if key in self._set: else False

    def put(self,key):
        key = hashlib.md5(key).hexdigest()

        if not self.exist(key):
            self._set.add(key)
            return True
        else:
            return False




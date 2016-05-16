#*-*coding:utf8*-*

import hashlib

import Araneae.db as DB

class BaseDupeFilter(object):

    def exist(self,key):
        raise NotImplementedError('去重器必须实现exist方法')

    def put(self,key):
        raise NotImplementedError('去重器必须实现put方法')

    #序列化和反序列化方法

class SingletonDupeFilter(BaseDupeFilter):

    def __init__(self):
        self._dupefilter = set()

    def exist(self,key):
        fingerprint = hashlib.md5(key).hexdigest()

        return True if fingerprint in self._dupefilter else False

    def put(self,key):
        fingerprint = hashlib.md5(key).hexdigest()

        if not self.exist(fingerprint):
            self._dupefilter.add(fingerprint)
            return True
        else:
            return False

class RedisDupeFilter(BaseDupeFilter):

    def def __init__(self,spider_name,**redis_conf):
        self._dupefilter_key = 'Dupefilter:' + spider_name
        self._dupefilter = DB.Redis(spider_name,**redis_conf)

    def exist(self,key):
        fingerprint = hashlib.md5(key).hexdigest()

        return True if self._dupefilter.sismember(self._dupefilter_key,fingerprint) else False

    def put(self,key):
        fingerprint = hashlib.md5(key).hexdigest()

        if not self.exist(fingerprint):
            self._dupefilter.sadd(self._dupefilter_key,fingerprint)
            return True
        else:
            return False




# coding:utf8

import redis

from Araneae.dupefilters import DupeFilter

class RedisDupeFilter(DupeFilter):

    def __init__(self, spider_name, redis):
        self._dupefilter_key = 'Dupefilter:{dupefilter_name}'.format(dupefilter_name=dupefilter_name)
        self._redis = redis

    @classmethod
    def from_spider(self, spider):
        dupefilter_name = spider.settings.get('SPIDER_NAME')
        dupefilter_conf = spider.settings.getdict('DUPEFILTER_CONF')
        redis = redis.StrictRedis(**dupefilter_conf)
        return cls(dupefilter_name, redis)

    def exist(self, key):
        return True if self._dupefilter.sismember(self._dupefilter_key, key) else False

    def put(self, key):
        """ 
        添加成功返回True,重复返回False
        """
        return self._dupefilter.sadd(self._dupefilter_key, key)

    def clear(self):
        return self._redis.delete(self._dupefilter_key)

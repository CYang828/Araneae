# coding:utf8


from Araneae.dupefilters import DupeFilter

class MemoryDupeFilter(DupeFilter):

    def __init__(self, dupefilter_name):
        self._dupefilter_key = 'Dupefilter:{dupefilter_name}'.format(dupefilter_name=dupefilter_name)
        self._dupefilter = set()

    @classmethod
    def from_spider(self, spider):
        dupefilter_name = spider.settings['SPIDER_NAME']
        return cls(dupefilter_name)

    def exist(self, key):
        return True if key in self._dupefilter else False

    def put(self, key):
        if not self.exist(key):
            self._dupefilter.add(key)
            return True
        else:
            return False

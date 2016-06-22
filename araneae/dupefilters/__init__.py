# coding:utf8


class DupeFilter(object):

    def exist(self, key):
        raise NotImplementedError

    def put(self, key):
        raise NotImplementedError

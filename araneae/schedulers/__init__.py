# coding:utf8


class Scheduler(object):

    def pull(self):
        raise NotImplementedError

    def push(self, r):
        raise NotImplementedError

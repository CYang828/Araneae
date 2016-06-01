#!coding:utf8

from Araneae.utils.livetracker import LiveObject

class Agent(LiveObject):

    def request(self,request):
        """
        请求request对象
        """
        raise NotImplementedError


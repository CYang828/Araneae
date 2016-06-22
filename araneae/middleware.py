#*-*coding:utf8*-*

import os
import random

import Araneae.man.exception as EXP
import Araneae.utils.setting as SET


class BaseMiddleware(object):
    pass


class RequestMiddleware(BaseMiddleware):
    def transport(self, request):
        raise NotImplementedError('reqeust middleware必须实现transport')


class DataMiddleware(BaseMiddleware):
    def transport(self, data):
        raise NotImplementedError('data middleware必须实现transport')


class FileMiddleware(BaseMiddleware):
    def transport(self, file_obj):
        raise NotImplementedError('file middleware必须实现transport')


class RandomMiddleWare(SET.Setting):
    __list = []
    __list_len = None
    __black_list = []

    def set_key(self, key):
        self.__list = self.getlist(key)
        self.__list_len = len(self.__list)

        if not self.__list_len:
            raise EXP.MiddlewareException('随机中间件中列表不能为空')

        return self.__list

    def random(self):
        random_idx = random.randrange(0, self.__list_len)
        return self.__list[random_idx]

    def add_black(self, item):
        self.__list.remove(item)
        self.__black_list.append(item)
        self.__list_len -= 1


class UserAgentMiddleware(RequestMiddleware, RandomMiddleWare):
    def __init__(self):
        super(UserAgentMiddleware, self).__init__('Araneae.man.user_agent')
        self.set_key('USER_AGENT')

    def transport(self, request):
        user_agent = self.random()
        request.set_user_agent(user_agent)
        return request


class ProxyMiddleware(RequestMiddleware, RandomMiddleWare):
    def __init__(self):
        super(ProxyMiddleware, self).__init__('Araneae.man.proxy')
        self.set_key('PROXY_IP')

    def transport(self, request):
        proxy = self.random()
        request.set_proxy(proxy)
        print request.json
        return request


if __name__ == '__main__':
    user_agent = UserAgent('Araneae.man.user_agent')
    print user_agent.random()

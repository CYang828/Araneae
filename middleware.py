#*-*coding:utf8*-*

import os
import random

import Araneae.man.exception as EXP
import Araneae.utils.setting as SET

class RandomMiddleWare(SET.Setting):
    __list = []
    __list_len = None
    __black_list = []
        
    def set_key(self,key):
        self.__list = self.getlist(key)
        self.__list_len = len(self.__list)

        if not self.__list_len:
            raise EXP.MiddlewareException('随机中间件中列表不能为空')

        return self.__list

    def random(self):
        random_idx = random.randrange(0,self.__list_len)
        return self.__list[random_idx]

    def add_black(self,item):
        self.__list.remove(item)
        self.__black_list.append(item)
        self.__list_len -= 1
        
class UserAgent(RandomMiddleWare):

    def __init__(self,module):
        super(UserAgent,self).__init__(module)
        self.set_key('USER_AGENT')

class ProxyIp(RandomMiddleWare):

    def __init__(self,module):
        super(UserAgent,self).__init__(module)
        self.set_key('PROXY_IP')

if __name__ == '__main__':
    user_agent = UserAgent('Araneae.man.user_agent')
    print user_agent.random()
    

        

    

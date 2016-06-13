# coding:utf8 

"""控制spider的动作,例如start,stop,包括一些拉取操作，上推操作....."""


class Engine(object):
    
    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    def pull_next_request(self):
        pass

    def push_next_request(self):
        pass

    

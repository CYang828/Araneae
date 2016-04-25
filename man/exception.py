#*-*coding:utf8*-*

class AraneaeException(Exception):

    def __init__(self,msg):
        self._msg = msg 

    def __str__(self):
        return repr(self._msg.encode('utf8'))

class MiddlewareException(AraneaeException):
    pass

class ChromesomeException(AraneaeException):
    pass

class DNAException(AraneaeException):
    pass





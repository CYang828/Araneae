#*-*coding:utf8*-*
"""
Araneae异常
"""

class AraneaeException(Exception):
    """所有异常的父类"""
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return self._msg

class SchedulerEmpty(AraneaeException):
    """调度器为空"""
    pass

class MiddlewareError(AraneaeException):
    """中间件错误"""
    pass


class ChromesomeError(AraneaeException):
    """配置文件错误"""
    pass


class DNAError(AraneaeException):
    """装载器错误"""
    pass


class RequestConnectionError(AraneaeException):
    """请求连接错误"""
    pass


class RequestError(AraneaeException):
    pass


class RequestTimeoutError(AraneaeException):
    pass


class RequestTooManyRedirectsError(AraneaeException):
    pass


class DownloaderError(AraneaeException):
    pass


class SchedulerError(AraneaeException):
    pass

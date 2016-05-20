#*-*coding:utf8*-*


class AraneaeException(Exception):
    def __init__(self, msg):
        self._msg = msg

    def __str__(self):
        return repr(self._msg.encode('utf8'))


class MiddlewareError(AraneaeException):
    pass


class ChromesomeError(AraneaeException):
    pass


class DNAError(AraneaeException):
    pass


class RequestConnectionError(AraneaeException):
    pass


class RequestErrorError(AraneaeException):
    pass


class RequestTimeoutError(AraneaeException):
    pass


class RequestTooManyRedirectsError(AraneaeException):
    pass

class DownloaderError(AraneaeException):
    pass

class SchedulerError(AraneaeException):
    pass

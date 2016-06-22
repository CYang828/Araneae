#*-*coding:utf8*-*

import re
import logging
from termcolor import colored

from araneae.utils.track import (get_meta_data,get_simple_meta_data)


class Logger(logging.Logger):
    """
    logging.Logger类实现,使用logging.getLogger(logger_name)获取对象.
    当构造函数name参数字符串以'.log'结尾时,写入文件.否则直接打印在console上.
    只有打印在console上的message才根据log_level区分颜色.
    """

    def __init__(self, name):
        logging.Logger.__init__(self, name, logging.DEBUG)
        self.__is_file = re.match(r'.+\.log$', name)

        if self.__is_file:
            self.__fhandler = logging.FileHandler(name)
        else:
            self.__fhandler = logging.StreamHandler()

        formatter = logging.Formatter("%(asctime)s [%(process)d:%(thread)d] [%(chain)s] %(message)s")
        self.__fhandler.setFormatter(formatter)
        self.addHandler(self.__fhandler)

    def debug(self, msg, *args, **kw):
        chain = get_meta_data()

        if self.__is_file:
            self.log(logging.DEBUG, "%s" % msg, extra={'chain': chain}, *args, **kw)
        else:
            colored_msg = colored(msg, color='green')
            self.log(logging.DEBUG, "%s" % colored_msg, extra={'chain': chain}, *args, **kw)

    def info(self, msg, *args, **kw):
        chain = get_simple_meta_data()

        if self.__is_file:
            self.log(logging.INFO, "%s" % msg, extra={'chain': chain}, *args, **kw)
        else:
            colored_msg = colored(msg, color='yellow')
            self.log(logging.INFO, "%s" % colored_msg, extra={'chain': chain}, *args, **kw)

    def warn(self, msg, *args, **kw):
        chain = get_simple_meta_data()

        if self.__is_file:
            self.log(logging.WARNING, "%s" % msg, extra={'chain': chain}, *args, **kw)
        else:
            colored_msg = colored(msg, color='blue')
            self.log(logging.WARNING, "%s" % colored_msg, extra={'chain': chain}, *args, **kw)

    def error(self, msg, *args, **kw):
        chain = get_meta_data()

        if self.__is_file:
            self.log(logging.ERROR, "%s" % msg, extra={'chain': chain}, *args, **kw)
        else:
            colored_msg = colored(msg, color='red')
            self.log(logging.ERROR, "%s" % colored_msg, extra={'chain': chain}, *args, **kw)

logging.setLoggerClass(Logger)

def get_logger(name):
    return logging.getLogger(name)



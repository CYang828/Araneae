#*-*coding:utf8*-*

import logging
from termcolor import colored


def set_logging(level,filename,fmt,datefmt):
    logging.basicConfig(level=level,
                    format=fmt,
                    datefmt=datefmt,
                    filename=filename)

#更换颜色
def color_string(string,color):
    return colored(string,color)

def Plog(msg,color = None):
    msg = color_string(msg,color = color) if color else msg
    print msg

def debug(msg,color = None):
    msg = color_string(msg,color = color) if color else msg
    logging.debug(msg)

def info(msg,color = None):
    msg = color_string(msg,color = color) if color else msg
    logging.info(msg)

def error(msg,color = None):
    msg = color_string(msg,color = color) if color else msg
    logging.error(msg)

def critical(msg,color = None):
    msg = color_string(msg,color = color) if color else msg
    logging.critical(msg)

#'%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
#'%a,%d %b %Y %H:%M:%S'

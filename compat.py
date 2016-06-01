#!coding:utf8

import six
import sys


try:
    import simplejson as json
except (ImportError,SyntaxError):
    #python3.2 不支持simplejson
    import json

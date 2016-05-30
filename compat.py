#!coding:utf8


import sys

_ver = sys.version_info

#python2
is_py2 = (_ver[0] == 2)

#python3
is_py3 = (_ver[0] == 3)

try:
    import simplejson as json
except (ImportError,SyntaxError):
    #python3.2 不支持simplejson
    import json

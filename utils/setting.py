#*-*coding:utf8*-*

import os
import six
import time
import random

from importlib import import_module

class Setting(object):
    """
    配置文件中,每一项可以是大写也可以是小写
    配置类中,所有的项都转换成大写存储,读取时可以通过大写或者小写进行读取
    配置选项都是用小写来存储
    """
    _options = {}
    _attributes = {}

    def __init__(self,module):
        self.set_from_module(module)

    def __getitem__(self,opt_name):
        opt_name = opt_name.upper()

        if opt_name in self._attributes:
            value = self._attributes[opt_name]
            return value
        else:
            return None

    def get(self,name,default = None):
        name = name.upper()
        value = self[name] if self[name] else default

        if name in self._options:
            if value.lower() in self._options[name]:
                return value
            else:
                raise TypeError('错误的配置项 -- key[%s] -- option[%s]' % (name,value))
        else:
            return value

    def getbool(self,name,default = False):
        return bool(int(self.get(name,default)))

    def getint(self,name,default = 0):
        return int(self.get(name,default))

    def getfloat(self,name,default = 0.0):
        return float(self.get(name,default))

    def getlist(self,name,default = None):
        return list(self.get(name,default))

    def getdict(self,name,default = None):
        return dict(self.get(name,default))

    def set_from_module(self,module):
        if isinstance(module,six.string_types):
            module = import_module(module)

        for key in dir(module): 
            self.set_from_value(key.upper(),getattr(module,key))

    def set_from_dict(self,values):
        for key,value in six.iteritems(values):
            self.set_from_value(key,value)

    def set_from_value(self,name,value):
        name = name.upper()
        self._attributes[name] = value
            
    def keys(self):
        return self._attributes.keys()

    def set_options(self,key,*values):
        key = key.upper()
        values = [value.lower() for value in values]
        self._options[key] = values

    def set_essential_keys(self,*keys):
        for key in keys:
            key = key.upper()
            if key not in self.keys():
                raise TypeError('必要的键%s' % key)

def revise_value(value):
    revise_value = []

    if isinstance(value,str):
        revise_value.append(value)
    elif isinstance(value,set):
        revise_value = dict(value)
    elif isinstance(value,list):
        revise_value = value

    return revise_value
        

if __name__ == '__main__':
    s = Setting('config')
    s.set_options('scheduler','redis','mq')
    print s.get('scheduler')

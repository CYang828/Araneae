#!coding:utf8

import os
import six
import time
import random

from importlib import import_module


class Settings(object):
    """
    配置文件中,每一项可以是大写也可以是小写
    配置类中,所有的项都转换成大写存储,读取时可以通过大写或者小写进行读取
    配置选项都是用小写来存储
    """
    _attributes = {}

    def __init__(self, module_name):
        self._module = None
        self._module_name = module_name
        self._attributes = {}
        self.reset()

    def reset(self):
        self._module = self.set_from_module(self._module_name)

    def __getitem__(self, opt_name):
        return self._attributes.get(opt_name.upper(),None)

    def set_from_module(self, module):
        self._module and reload(self._module)

        if isinstance(module, six.string_types):
            module = import_module(module)

        for key in dir(module):
            self.set_from_value(key.upper(), getattr(module, key))

        return module

    def get(self, name, default=None, dont_empty=False, options=None):
        value = self[name] if self[name] else default

        if dont_empty and not value:
            raise TypeError('配置项不能为空')

        if options and value.lower() not in options:
            raise TypeError('配置项的值不在选项列表内')
            
        return value

    def getbool(self, name, default=False, dont_empty=False, options=None):
        return bool(int(self.get(name, default)))

    def getint(self, name, default=0, dont_empty=False, options=None):
        return int(self.get(name, default))

    def getfloat(self, name, default=0.0, dont_empty=False, options=None):
        return float(self.get(name, default))

    def getlist(self, name, default=[], dont_empty=False,options=None):
        return list(self.get(name, default))

    def getdict(self, name, default={}, dont_empty=False,options=None):
        return dict(self.get(name, default))

    def set_from_dict(self, values):
        for key, value in six.iteritems(values):
            self.set_from_value(key, value)

    def set_from_value(self, name, value):
        name = name.upper()
        self._attributes[name] = value

    def keys(self):
        return self._attributes.keys()

    def iterater(self):
        return self._attributes.iteritems()
        

if __name__ == '__main__':
    import time
    s = Settings('config')
    print s.get('scheduler')
    time.sleep(20)
    s.reset()
    print s.get('scheduler')
    #s.get('cant_be_empty',dont_empty=True)
    #print s.get('opt',options = ['name','age','sex'])
    #print s.get('opt',options = ['name1','age','sex'])

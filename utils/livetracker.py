#!coding:utf8

from __future__ import print_function

import six
import weakref

from time import time
from operator import itemgetter
from collections import defaultdict


NoneType = type(None)
#弱引用,不影响正常的垃圾回收
live_objs = defaultdict(weakref.WeakKeyDictionary)

class LiveObject(object):
    """需要跟踪生命周期的对象可以继承此类"""
    
    __slots__ = ()

    def __new__(cls,*args,**kwargs):
        obj = object.__new__(cls)
        live_objs[cls][obj] = time()
        return obj


def format_live_objs(ignore = NoneType):
    s = "Live objs\n\n" 
    now = time()

    for cls, wdict in sorted(six.iteritems(live_objs),key=lambda x: x[0].__name__):
        if not wdict:
            continue

        if issubclass(cls, ignore):
            continue

        oldest = min(six.itervalues(wdict))
        s += "%-30s %6d   oldest: %ds ago\n" % (cls.__name__, len(wdict), now - oldest)

    return s


def print_live_objs(ignore = NoneType):
    print(format_live_objs(ignore))


def get_oldest(class_name):
    for cls,wdict in six.iteritems(live_objs):
        if cls.__name__  == class_name:
            if not wdict:
                break
            return min(six.iteritems(wdict), key = itemgetter(1))[0]


def iter_all(class_name):
    for cls, wdict in six.iteritems(live_objs):
        if cls.__name__ == class_name:
            return six.iterkeys(wdict)


if __name__ == '__main__':
    from time import sleep

    class A(LiveObject):
        pass

    class B(LiveObject):
        pass

    a = A()
    b = B()
    sleep(3)
    a1 = A()
    a2 = A()
    b1 = B()
    b2 = B()
    b3 = B()
    print(get_oldest('B'))
    print('--------------')
    print_live_objs()
    print('--------------')
    for obj in iter_all('A'):
        print(obj)
        

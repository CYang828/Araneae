# coding:utf8

import weakref
from parsel import Selector
from lxml.html import soupparser


_selector_cache = weakref.WeakKeyDictionary()

def response_to_selector(response):
    """Selector expects text to be an unicode object in Python 2 or an str object in Python 3"""

    cache = _selector_cache.setdefault(response, None)
    
    if not cache:
        root = soupparser.fromstring(response.text, features='html5lib')  
        cache = Selector(root=root)
        _selector_cache[response] = cache

    return cache



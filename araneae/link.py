# coding:utf8

import six

from araneae.http import Request
#from araneae.datas import Data
from araneae.utils.log import get_logger
from araneae.utils.python import to_bytes



logger = get_logger(__name__)

class Link(object):
    """Link对象"""

    __slots__ = ['url', 'text', 'fragment', 'nofollow','request','data']

    def __init__(self, url, text='', fragment='', nofollow=False):
        if not isinstance(url, str):
            if six.PY2:
                logger.warn("Link urls must be str objects. "
                              "Assuming utf-8 encoding (which could be wrong)")
                url = to_bytes(url, encoding='utf8')
            else:
                got = url.__class__.__name__
                raise TypeError("Link urls must be str objects, got %s" % got)

        self.url = url
        self.text = text
        self.fragment = fragment
        self.nofollow = nofollow
        self.request = Request(url)
        #self.data = Data(text)

    def __eq__(self, other):
        return self.url == other.url and self.text == other.text and \
               self.fragment == other.fragment and self.nofollow == other.nofollow

    def __hash__(self):
        return hash(self.url) ^ hash(self.text) ^ hash(self.fragment) ^ hash(self.nofollow)

    def __repr__(self):
        return 'Link(url=%r, text=%r, fragment=%r, nofollow=%r)' % \
               (self.url, self.text, self.fragment, self.nofollow)

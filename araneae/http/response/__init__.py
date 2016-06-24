#!coding:utf8

import weakref
from w3lib import html
from parsel import Selector
from lxml.html import soupparser
from requests.models import Response as RequestsResponse

from araneae.utils.livetracker import LiveObject
from araneae.utils.python import (to_unicode,to_bytes)

class Response(LiveObject,RequestsResponse):

    _baseurl_cache = weakref.WeakKeyDictionary()

    def __init__(self,requests_response):
        assert isinstance(requests_response,RequestsResponse), 'Response的参数必须为requests返回的response: [%s]' % type(requests_response).__name__
        self._response = requests_response
        self.set_selector()
        self.set_url()
        self.set_encoding()

    def  __str__(self):
        return self._response.__repr__()

    __repr__ = __str__

    def set_selector(self):
        root = soupparser.fromstring(self._response.text, features='html5lib')
        self.selector = Selector(root=root)

    def set_url(self):
        self.url = self._response.url

    def set_encoding(self):
        self.encoding = self._response.encoding

    def content(self):
        return to_bytes(self._response.content)

    def text(self):
        return to_unicode(self._response.text)

    def get_base_url(self):
        """Return the base url of the given response, joined with the response url"""
        if self._response not in self._baseurl_cache:
            text = self._response.text[0:4096]
            self._baseurl_cache[self] = html.get_base_url(text, self._response.url, self._response.encoding)

        return self._baseurl_cache[self]



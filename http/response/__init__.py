#!coding:utf8

import weakref
from w3lib import html
from requests.models import Response as RequestsResponse

from Araneae.utils.livetracker import LiveObject
from Araneae.utils.python import (to_unicode,to_bytes)

class Response(LiveObject,RequestsResponse):

    _baseurl_cache = weakref.WeakKeyDictionary()

    def __init__(self,requests_response):
        assert isinstance(requests_response,RequestsResponse), 'Response的参数必须为requests返回的response: [%s]' % type(requests_response).__name__
        self._response = requests_response

    def  __str__(self):
        return self._response.__repr__()

    __repr__ = __str__

    def content(self):
        return to_bytes(self._response.content)

    def text(self):
        return to_unicode(self._response.text)

    def get_base_url(self):
        """Return the base url of the given response, joined with the response url"""
        if response not in _baseurl_cache:
            text = self._response.text[0:4096]
            _baseurl_cache[self] = html.get_base_url(text, self._response.url, self._response.encoding)

        return _baseurl_cache[self]


if __name__ == '__main__': 
    from requests import get
    res = get('http://www.baidu.com')
    r = Response(res)   
    print r
    #print r.content()
    print r.text()

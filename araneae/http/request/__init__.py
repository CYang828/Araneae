#!coding:utf8

import six
import hashlib
import weakref 
from w3lib.url import safe_url_string


from araneae.compat import json as Json
from araneae.utils.python import to_bytes
from araneae.utils.livetracker import LiveObject
from araneae.constant import DEFAULT_REQUEST_METHOD
from araneae.utils.url import (escape_ajax,guess_scheme,canonicalize_url,get_scheme)


class Request(LiveObject):
    """request对象,如果已经计算过printfinger则会在缓存中寻找,不会重新计算"""

    _fingerprint_cache = weakref.WeakKeyDictionary()

    def __init__(self, url, callback = None, method = DEFAULT_REQUEST_METHOD, encoding = 'utf8', proxies = None,
                 headers = None, data = None, params = None,auth = None,cookies = None,files = None,
                 json = None,dont_filter = False, errback = None,hooks = None):
        self._encoding = encoding
        self.method = str(method).upper()
        self._set_url(url)
        self._set_scheme(url)
        self.data = data
        self.proxies = proxies or {}
        self.params = params or {}
        self.json = json or {}
        self.auth = auth or {}

        assert callback or not errback, 'Request不能在没有callback的情况下使用errback'
        self.callback = callback
        self.errback = errback

        self.headers = headers or {}
        self.cookies = cookies or {}
        self.files = files or {}
        self.hooks = files or {}
        
        self.dont_filter = dont_filter

    def __str__(self):
        return '<Request %s %s>' % (self.method,self.url)

    __repr__ = __str__

    def _set_url(self,url):
        if not isinstance(url, six.string_types):
            raise TypeError('Ruquest url必须是字符串或者unicode,[%s]' % type(url).__name__)

        safe_url = safe_url_string(url,self._encoding)
        # 如果网站支持,获取网页的snapshot
        self.url = escape_ajax(safe_url)

        # 如果网址中有文件路径,补全为file://,否则补全为http://
        if ':' not in self.url:
            self.url = guess_scheme(self.url)

    def _set_scheme(self,url):
        self.scheme = get_scheme(url)

    def copy(self):
        return self.replace()

    def to_json(self):
        return {'url':self.url,'scheme':self.scheme,'method':self.method,'encoding':self._encoding,'callback':self.callback,
                'proxies':self.proxies,'headers':self.headers,'data':self.data,'params':self.params,
                'auth':self.auth,'cookies':self.cookies,'json':self.json,
                'dont_filter':self.dont_filter,'errback':self.errback}

    def to_json_string(self):
        return Json.dumps(self.to_json(),ensure_ascii = True)

    def to_printfinger(self, include_headers = None):
        if include_headers:
            include_headers = tuple(to_bytes(header.lower()) for header in sorted(include_headers))

        cache = self._fingerprint_cache.setdefault(self, {})

        if include_headers not in cache:
            fp = hashlib.sha1()
            fp.update(to_bytes(self.method))
            fp.update(to_bytes(canonicalize_url(self.url)))
            fp.update(self.data or b'')

            if include_headers:
                for hdr in include_headers:
                    if hdr in request.headers:
                        fp.update(hdr)
                        for v in request.headers.getlist(hdr):
                            fp.update(v)
            cache[include_headers] = fp.hexdigest()

        return cache[include_headers] 
            
    def replace(self, *args, **kwargs):
        for x in ['url','callback','method','encoding','proxies','priority','headers',
                  'data','params','auth','cookies','json','dont_filter','errback']:
            kwargs.setdefault(x, getattr(self,x))

        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    @property
    def encoding(self):
        return self._encoding


if __name__ == '__main__':
    request = Request('www.baidu.com')
    print request
    print request.to_printfinger()

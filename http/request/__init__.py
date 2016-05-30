#!coding:utf8
import sys
sys.path.append('/home/zhangchunyang/Araneae')
print sys.path

import time
import urllib
import hashlib
import requests

import Araneae.utils.http as UTLH
import Araneae.man.exception as EXP
from Araneae.compat import json as Json
from Araneae.utils.livetracker import LiveObject
from Araneae.utils.url import (safe_url_string,escape_ajax)

DEFAULT_REQUEST_METHOD = 'GET'
DEFAULT_REQUEST_TIMEOUT = 2
DEFAULT_CALLBACK = 'parse'
DEFAULT_ASSOCIATE = False

class Request(LiveObject):

    def __init__(self, url, callback = None, method = DEFAULT_REQUEST_METHOD, encoding = 'utf8', proxies = None,
                 headers = None, data = None, params = None,auth = None,cookies = None,
                 json = None,dont_filter = False, errback = None):
        self._encoding = encoding
        self.method = str(method).upper()
        self._set_url(url)
        self._data = data
        assert isinstance(priority,int), 'Request优先级必须是int' % priority
        self._priority = priority
        self._proxies = proxies or {}
        self._params = params or {}
        self._json = json or {}
        self._auth = auth or {}

        assert callback or not errback, 'Request不能在没有callback的情况下使用errback'
        self.callback = callback
        self.errback = errback

        self.headers = headers or {}
        self.cookies = cookies or {}
        
        self.dont_filter = dont_filter

    def __str__(self):
        return '<%s %s>' % (self.method,self._url)

    __repr__ = __str__

    def _set_url(self,url):
        if not isinstance(url, six.string_types):
            raise TypeError('Ruquest url必须是字符串或者unicode,[%s]' % type(url).__name__)

        safe_url = safe_url_string(url,self._encoding)
        #如果网站支持,获取网页的snapshot
        self._url = escape_ajax(safe_url)

        #如果网址没有schema,自动补全为http://
        if ':' not in self._url:
            self._url = autocomplete_url_schema(self._url)

    def copy(self):
        return self.replace()

    def to_json(self):
        return {'url':self._url,'method':self.method,'encoding':self._encoding,'callback':self.callback,
                'proxies':self._proxies,'headers':self.headers,'data':self._data,'params':self._params,
                'auth':self._auth,'cookies':self.cookies,'json':self._json,
                'dont_filter':self.dont_filter,'errback':self.errback}

    def to_json_string(self):
        return Json.dumps(self.to_json(),ensure_ascii = True)

    @classmethod
    def replace(cls, *args, **kwargs):
        for x in ['url','callback','method','encoding','proxies','priority','headers',
                  'data','params','auth','cookies','json','dont_filter','errback']:
            kwargs.setdefault(x, getattr(self,x))
            return cls(*args, **kwargs)

    @property
    def encoding(self):
        return self._encoding

    @property
    def url(self):
        return self._url


if __name__ == '__main__':
    pass

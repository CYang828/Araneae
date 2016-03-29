#*-*coding:utf8*-*
import sys
sys.path.append('..')

print sys.path
del sys

import json
import time
import urllib
import hashlib
import requests

import Araneae.utils.http as utils_http

DEFAULT_TIMEOUT = 2

class Request(object):

    def __init__(self,url,**args):
        """
        url:统一资源定位符
        method:方式
        headers:头信息
        body:包体信息
        cookies:cookie信息
        callback:回调函数对象
        timeout:超时时间
        """
        if not url:
            raise TypeError

        self._url = utils_http.revise_url(url)
        self._method = utils_http.validate_method(args.get('method','GET')) 
        self._headers = args.get('headers',None)
        self._body = args.get('body',None)
        self._cookies = args.get('cookies',None)
        self._callback = args.get('callback',None)
        self._timeout = args.get('timeout',DEFAULT_TIMEOUT)

        self._json = ''
        self._sequence_json()

    def fetch(self):
        """
        抓取页面信息
        """
        method = self._method.lower()
        response = getattr(requests,method)(self._url,data = self._body,headers = self._headers,cookies = self._cookies,timeout = self._timeout)
        return response

    @property
    def json(self):
        return self._json

    @property
    def callback(self):
        return self._callback

    #这个是用来放到mq中的
    def _sequence_json(self):
        request_json = {}
        request_json['url'] = self._url

        if self._method:
            request_json['method'] = self._method
        if self._headers:
            request_json['headers'] = self._headers
        if self._body:
            request_json['body'] = self._body
        if self._cookies:
            request_json['cookies'] = self._cookies
        if self._callback:
            request_json['callback'] = self._callback

        self._json = json.dumps(request_json)

def json2request(request_json):
    """
    将json转成Request对象
    """
    request_json = json.loads(request_json)
    request = Request(**request_json)
    return request

if __name__ == '__main__':
    r = Request('http://www.baidu.com',method = 'POST')
    res = r.fetch()
    print time.time()
    print r.fingerprinter()
    print time.time()

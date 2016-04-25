#*-*coding:utf8*-*
import json
import time
import urllib
import hashlib
import requests

import Araneae.utils.http as UTLH

DEFAULT_TIMEOUT = 2

class Request(object):

    def __init__(self,spider_name,url,rule_number,**args):
        """
        spider_name:爬虫名
        url:统一资源定位符
        method:方式
        headers:头信息
        data:提交数据
        cookies:cookie信息
        callback:回调函数对象
        """
        if not url:
            raise TypeError
        
        self._spider_name = spider_name
        self._url = UTLH.revise_url(url)
        self._method = UTLH.validate_method(args.get('method','GET')) 
        self._headers = args.get('headers',{})
        self._data = args.get('data',{})
        self._cookies = args.get('cookies',{})
        self._callback = args.get('callback','parse')
        self._auth = args.get('auth',{})
        self._proxy = args.get('proxy',None)

        self._rule_number = rule_number
        self._fid = args.get('fid')

        self._json = ''

    def fetch(self,timeout = DEFAULT_TIMEOUT):
        """
        抓取页面信息
        """
        method = self._method.lower()
        #?????????????????????添加错误处理,外部将错误链接重新添加回调度器
        response = getattr(requests,method)(self._url,proxies = self._proxy,data = self._data,headers = self._headers,cookies = self._cookies,timeout = timeout)
        return response

    def set_rule_number(self,rule_number):
        self._rule_number = rule_number

    def set_headers(self,header_dict):
	    self._headers = dict(self._headers,**header_dict)

    def set_cookies(self,cookie_dict):
	    self._cookies = dict(self._cookies,**cookie_dict)

    def set_auth(self,auth_dict):
	    self._auth = dict(self._auth,**auth_dict)

    def set_user_agent(self,user_agent):
        self._headers['User-Agent'] = user_agent

    def set_http_proxy(self,proxy):
        self._proxy = {'http':proxy}

    def set_https_proxy(self,proxy):
        self._proxy = {'https':proxy}

    @property
    def fid(self):
        return self._fid

    @fid.setter
    def fid(self,fid):
        self._fid = fid

    @property
    def url(self):
        return self._url

    @property
    def method(self):
        return self._method

    @property
    def rule_number(self):
        return self._rule_number

    @rule_number.setter
    def rule_number(self,rule_number):
        self._rule_number = rule_number

    @property
    def headers(self):
        return self._headers

    @property
    def cookies(self):
        return self._cookies

    @property
    def data(self):
        return self._data

    @property
    def callback(self):
        return self._callback

    @callback.setter
    def callback(self,callback):
        self._callback = callback

    @property
    def json(self):
        self._sequence_json()
        return self._json

    #这个是用来放到mq中的
    def _sequence_json(self):
        request_json = {}
        request_json['url'] = self._url

        if self._spider_name:
            request_json['spider_name'] = self._spider_name

        if self._method:
            request_json['method'] = self._method
        if self._headers:
            request_json['headers'] = self._headers
        if self._data:
            request_json['data'] = self._data
        if self._cookies:
            request_json['cookies'] = self._cookies
        if self._callback:
            request_json['callback'] = self._callback

        request_json['rule_number'] = self._rule_number
        
        if self._fid:
            request_json['fid'] = self._fid

        self._json = json.dumps(request_json)

def json2request(request_json):
    """
    将Medium的json穿转换成request
    """
    request_json = json.loads(request_json)
    request = Request(**request_json)
    return request

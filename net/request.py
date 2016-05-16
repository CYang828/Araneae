#*-*coding:utf8*-*
import json
import time
import urllib
import hashlib
import requests

import Araneae.utils.http as UTLH
import Araneae.man.exception as EXP

DEFAULT_REQUEST_TIMEOUT = 2
DEFAULT_CALLBACK = 'parse'
DEFAULT_ASSOCIATE = False

class Request(object):
    """
    spider_name:爬虫名
    url:统一资源定位符
    method:方式
    headers:头信息
    data:提交数据
    cookies:cookie信息
    callback:回调函数对象
    auth:认证
    proxies:代理
    associate:是否关联
    """

    __spider_name = ''
    __url = ''
    __method = 'get'
    __data = {}
    __cookies = {}
    __auth = {}
    __proxies = {}
    __callback = None
    __fid = None
    __rule_number = None
    __associate = False

    def __init__(self,url,**args):
        if not url:
            raise EXP.RequestException('request对象必须有url')
        
        self.__url = UTLH.revise_url(url)

        self.__method = UTLH.validate_method(args.get('method','GET')) 
        self.__headers = args.get('headers',{})
        self.__data = args.get('data',{})
        self.__cookies = args.get('cookies',{})
        self.__auth = args.get('auth',{})
        self.__proxies = args.get('proxies',None)

        self.__spider_name = args.get('spider_name','')
        self.__fid = args.get('fid',None)
        self.__rule_number = args.get('rule_number',None)
        self.__callback = args.get('callback',DEFAULT_CALLBACK)
        self.__associate = args.get('associate',DEFAULT_ASSOCIATE)

    def _sequence_json(self):
        request_json = {}
        request_json['url'] = self.__url

        if self.__spider_name:
            request_json['spider_name'] = self.__spider_name

        if self.__method:
            request_json['method'] = self.__method
        if self.__headers:
            request_json['headers'] = self.__headers
        if self.__data:
            request_json['data'] = self.__data
        if self.__cookies:
            request_json['cookies'] = self.__cookies
        if self.__auth:
            request_json['auth'] = self.__auth
        if self.__proxies:
            request_json['proxies'] = self.__proxies

        if self.__callback:
            request_json['callback'] = self.__callback
        if self.__fid:
            request_json['fid'] = self.__fid

        if not self.__rule_number:
            raise EXP.RequestException('request对象必须设置rule number')

        request_json['rule_number'] = self.__rule_number

        request_json['associate'] = self.__associate

        return json.dumps(request_json,ensure_ascii = False)

    def set_spider_name(self,spider_name):
        self.__spider_name = spider_name
        return self

    def set_rule_number(self,rule_number):
        self.__rule_number = rule_number
        return self

    def set_fid(self,fid):
        self.__fid = fid
        return self

    def set_auth(self,auth):
        self.__auth = auth
        return self

    def set_user_agent(self,user_agent):
        self.__headers['User-Agent'] = user_agent
        return self

    def set_http_proxy(self,proxy):
        self.__proxy = {'http':proxy}
        return self

    def set_https_proxy(self,proxy):
        self.__proxy = {'https':proxy}
        return self

    def set_associate(self,associate):
        self.__associate = associate
        return self

    def add_headers(self,header_dict):
        self.__headers = dict(self._headers,**header_dict)
        return self

    def add_cookies(self,cookie_dict):
        self.__cookies = dict(self._cookies,**cookie_dict)
        return self

    def fetch(self,timeout = DEFAULT_REQUEST_TIMEOUT):
        """
        抓取页面信息
        """
        try:
            response = getattr(requests,self.__method)(self.__url,proxies = self.__proxies,data = self.__data,headers = self.__headers,cookies = self.__cookies,timeout = timeout)
        except requests.exceptions.ConnectionError:
            raise EXP.RequestConnectionException('DNS查询失败或者拒绝连接')
        except requests.exceptions.HTTPError:
            raise EXP.RequestErrorException('无效HTTP响应')
        except requests.exceptions.Timeout:
            raise EXP.RequestTimeoutException('请求超时')
        except requests.exceptions.TooManyRedirects:
            raise EXP.RequestTooManyRedirectsException('超过最大重定向次数')

        return response

    @property
    def url(self):
        return self.__url

    @property
    def method(self):
        return self.__method

    @property
    def rule_number(self):
        return self.__rule_number

    @rule_number.setter
    def rule_number(self,rule_number):
        self.__rule_number = rule_number

    @property
    def headers(self):
        return self.__headers

    @property
    def cookies(self):
        return self.__cookies

    @property
    def data(self):
        return self.__data

    @property
    def callback(self):
        return self.__callback

    @callback.setter
    def callback(self,callback):
        self.__callback = callback

    @property
    def json(self):
        return self._sequence_json()

    @property
    def fid(self):
        return self.__fid

    @fid.setter
    def fid(self,fid):
        self.__fid = fid

    @property
    def associate(self):
        return self.__associate

    @associate.setter
    def associate(self,associate):
        self.__associate = associate

def json2request(request_json):
    """
    json串转换成request对象
    """
    request_json = json.loads(request_json)
    request = Request(**request_json)
    return request

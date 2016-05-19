#*-*coding:utf8*-*

import json

class File(object):
    __url = None
    __method = None
    __file_name = None
   
    def __init__(self,url,file_name,**kvargs):
        self.__url = url
        self.__file_name = file_name
        self.__method = kvargs.get('method','get')

        self._cookies = kvargs.get('cookies',{})
        self._headers = kvargs.get('headers',{})
        self._proxies = kvargs.get('proxies',{})
        self._auth = kvargs.get('auth',{})
        self._data = kvargs.get('data',{})

    def __str__(self):
        return self._sequence_json()

    def _sequence_json(self):
        file_json = {}

        if self.__url:
            file_json['url'] = self.__url

        if self.__method:
            file_json['method'] = self.__method

        if self.__file_name:
            file_json['file_name'] = self.__file_name

        if self._cookies:
            file_json['cookies'] = self._cookies

        if self._headers:
            file_json['headers'] = self._headers

        if self._proxies:
            file_json['proxies'] = self._proxies

        if self._data:
            file_json['data'] = self._data

        file_json = json.dumps(file_json,ensure_ascii = True)

        return file_json

    def set_user_agent(self,user_agent):
        self.__headers['User-Agent'] = user_agent

    def set_http_proxy(self,proxy):
        self.__proxies = {'http':proxy}

    def set_https_proxy(self,proxy):
        self.__proxies = {'https':proxy}

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self,url):
        self.__url = value

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self,method):
        self.__method = method

    @property
    def cookies(self):
        return self._cookies

    @property
    def file_name(self):
        return self.__file_name

    @file_name.setter
    def file_name(self,file_name):
        self.__file_name = file_name

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self,header):
        self._headers = dict(self._headers,**header)

    @property
    def proxies(self):
        return self._proxies

    @property
    def json(self):
        return self._sequence_json()

    @classmethod
    def instance(cls,file_json):
        file_json = json.loads(file_json)
        return cls(**file_json)

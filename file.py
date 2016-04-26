#*-*coding:utf8*-*

class File(object):
    __url = None
    __cookies = None
    __method = None
    __file_name = None
   
    def __init__(self,**kvargs):
        self.__url = kvargs.get('url')
        self.__method = kvargs.get('method')
        self.__cookies = kvargs.get('cookie')
        self.__file_path = kvargs.get('file_path')
        self.__headers = kvargs.get('header')
        self.__proxies = kvargs.get('proxy')

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
    def cookie(self):
        return self.__cookies

    @cookie.setter
    def cookie(self,cookies):
        self.__cookies =cookies 

    @property
    def file_path(self):
        return self.__file_path

    @file_path.setter
    def file_path(self,file_path):
        self.__file_path = file_path

    @property
    def method(self):
        return self.__method

    @method.setter
    def method(self,method):
        self.__method = method

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self,header):
        self.__headers = dict(self.__headers,**header)

    @property
    def proxies(self,proxy):
        return self.__proxies


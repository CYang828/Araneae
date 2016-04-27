#*-*coding:utf8*-*

class File(object):
    __url = None
    __method = None
    __file_name = None
   
    def __init__(self,**kvargs):
        self.__url = kvargs.get('url')
        self.__method = kvargs.get('method','get')
        self.__file_path = kvargs.get('file_path')

        self._cookies = kvargs.get('cookies')
        self._headers = kvargs.get('headers')
        self._proxies = kvargs.get('proxies')
        self._auth = kvargs.get('auth')

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
    def file_path(self):
        return self.__file_path

    @file_path.setter
    def file_path(self,file_path):
        self.__file_path = file_path

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self,header):
        self._headers = dict(self._headers,**header)

    @property
    def proxies(self,proxy):
        return self.__proxies

    def json(self):
        file_json = {}

        if self.__url:
            file_json['url'] = self.__url

        if self.__method:
            file_json['method'] = self.__method

        if self.__cookies:
            file_json['cookie'] = self.__cookies

        if self.__file_path:
            file_json['file_path'] = self.__file_path

        if self.__headers:
            file_json['header'] = self.__headers

        if self.__proxies:
            file_json['proxy'] = self.__proxies

        file_json = json.dumps(file_json,ensure_ascii = True)

        return file_json

    @classmethod
    def instance(cls,json):
        json = json.loads(json)
        return cls(**json)

#*-*coding:utf8*-*

import re
import lxml.html
import lxml.html.soupparser

class BaseExtractor(object):
    __dom = None

class UrlExtractor(BaseExtractor):

    def __init__(self,dom,**args):
        self.__dom = dom
        self._allow_regex = [re.compile(regex) for regex in args.get('allow',[])]
        self._deny_regex = [re.compile(regex) for regex in args.get('deny',[])]
        self._headers = args.get('headers',None)
        self._cookies = args.get('cookies',None)
        self._method = args.get('method','GET')
        self._body = args.get('body',None)

        self._urls = []
        self._allow_urls = []
        self._extract_urls()
        self._extract_allow_urls()
        self._extract_deny_urls()

    def __call__(self):
        return self._allow_urls
    
    def extract(self):
        return self._allow_urls

    def _extract_urls(self):
        self._urls = self.__dom.xpath('//a//@href')

    def _extract_allow_urls(self):
        allow_urls_tmp = self._urls

        for allow in self._allow_regex:
            allow_urls_tmp = [url for url in allow_urls_tmp if allow.match(url)] 

        self._allow_urls = allow_urls_tmp

    def _extract_deny_urls(self):
        allow_urls_tmp = self._allow_urls

        for deny in self._deny_regex:
            allow_urls_tmp = [url for url in allow_urls_tmp if not deny.match(url)] 

        self._allow_urls = allow_urls_tmp

    @property
    def urls(self):
        return self._urls

    @property
    def allow_urls(self):
        return self._allow_urls

class URLFormatExtractor(BaseExtractor):
    pass

class DataExtractor(BaseExtractor):
    
    def __init__(self,dom,css = None,xpath = None):
        self.__dom = dom
        self._css = [c for c in css]
        self._xpath = [x for x in xpath]
        self._xpath_result = None
        self._css_result = None

        if xpath:
            self._xpath()

        if css:
            self._css()

        if not xpath and not css:
            raise TypeError('必须提供一个参数')

    def __call__(self,type = None):
        if not type:
            return {'xpath':self._xpath_result,'css':self._css_result}
        elif type == 'xpath':
            return self._xpath_result
        elif type == 'css':
            return self._css_reuslt

    def _xpath(self):
        result = []
        
        for x in self._xpath:
            result.append(self.__dom.xpath(x))

        self._xpath_result = result


    def _css(self):
        result = []

        for c in self._css:
            result.append(self.__dom.cssselect(c))

        self._css_result = result

    def extract_xpath(self):
        return self._xpath_result

    def extract_css(self):
        return self._css_result

    @property
    def xpath_data(self):
        return self._xpath_result

    @property
    def css_data(self):
        return self._css_result

def response2dom(response):
    try:
        dom = lxml.html.fromstring(response.text)
    except UnicodeDecodeError:
        dom = lxml.html.soupparser.fromstring(response.text)

    return dom

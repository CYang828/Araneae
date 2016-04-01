#*-*coding:utf8*-*

import re
import lxml.html
import lxml.html.soupparser

import Araneae.utils.http as UTL
import Araneae.net.request as REQ
import Araneae.utils.setting as SET

class BaseExtractor(object):
    __dom = None
    __response_url = ''

class UrlExtractor(BaseExtractor):
    """
    一个UrlExtractor只是针对一个response存在的,一个response对象可以对应有多个extractor
    """

    def __init__(self,(dom,response_url),page_rule):
        self.__rule = page_rule
        self.__response_url = response_url
        self.__dom = dom
        args = page_rule.extract_url_element
        self._allow_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(args.get('allow',[]))]
        self._deny_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(args.get('deny',[]))]
        self._headers = args.get('headers',None)
        self._cookies = args.get('cookies',None)
        self._method = args.get('method','GET')
        self._body = args.get('body',None)

        self._urls = []
        self._allow_urls = []
        self._allow_requests = []
        self._extract_urls()
        self._extract_allow_urls()
        self._url2request()

    def __call__(self):
        return self._allow_requests
    
    def extract(self):
        return self._allow_urls

    def _extract_urls(self):
        self._urls = self.__dom.xpath('//a//@href')

    def _extract_allow_urls(self):
        """
        每一个url存在3种状态,deny(2) > allow(1) > unmark(0),在不同的情况下选择展现的url不同(这种代码量少,复杂度高)

        """
        #如果允许和阻止的规则都没有,则返回当前页面全部url
        if not self._allow_regexes and not self._deny_regexes:
            self._allow_urls = self._urls
            return
        
        #如果有阻止规则没有允许规则,则返回阻止规则剩下的全部url
        if not self._allow_regexes and self._deny_regexes:
            deny_list = []

            for idx,url in enumerate(self._urls):
                for deny_regex in self._deny_regexes:
                    if deny_regex.match(url):
                        deny_list.append(idx)
                        break

            for deny_idx in deny_list:
                del self._urls[deny_idx]

            print 'DENY_LIST:' + str(deny_list)

            self._allow_urls = self._urls
            return 
            
        #如果允许和阻止的规则都有,则返回允许并不被阻止的url
        #如果有允许规则没有阻止规则,则返回允许规则的url
        if self._allow_regexes and self._deny_regexes:
            for idx,url in enumerate(self._urls):
                is_deny = False

                #先确定是否禁止
                for deny_regex in self._deny_regexes:
                    if deny_regex.match(url):
                        is_deny = True
                        #print 'DENY:' + url
                        break

                if not is_deny:                   
                    for allow_regex in self._allow_regexes:
                        if allow_regex.match(url):
                            #print 'ALLOW:' + url
                            self._allow_urls.append(url)
                            break
            
            return 

    def _url2request(self):
        request_args = {'method':self._method,'headers':self._headers,'cookies':self._cookies,'body':self._body}

        for url in self._allow_urls:
            request = REQ.Request(UTL.replenish_url(self.__response_url,url),rule_number = self.__rule.number+1,**request_args)
            self._allow_requests.append(request)

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

    return (dom,response.url)

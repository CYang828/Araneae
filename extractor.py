#*-*coding:utf8*-*

import re
import itertools
import lxml.html
import lxml.html.soupparser

import Araneae.data as DT
import Araneae.utils.http as UTL
import Araneae.net.request as REQ
import Araneae.utils.setting as SET

import sys
reload(sys)
sys.setdefaultencoding('utf8')

class BaseExtractor(object):
    __dom = None
    __response_url = ''

class UrlExtractor(BaseExtractor):
    """
    一个UrlExtractor只是针对一个response存在的,一个response对象可以对应有多个extractor
    """

    def __init__(self,dom,response_url,page_rule,fid):
        self.__rule = page_rule
        self.__dom = dom
        self.__response_url = response_url
        args = page_rule.extract_url_element
        self._allow_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(args.get('allow',[]))]
        self._deny_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(args.get('deny',[]))]
        self._headers = args.get('headers',None)
        self._cookies = args.get('cookies',None)
        self._method = args.get('method','GET')
        self._data = args.get('data',None)

        self._fid = fid

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
        request_args = {'method':self._method,'headers':self._headers,'cookies':self._cookies,'data':self._data,'fid':self._fid}

        for url in self._allow_urls:
            request = REQ.Request(UTL.replenish_url(self.__response_url,url),rule_number = self.__rule.number+1,**request_args)
            self._allow_requests.append(request)

    @property
    def urls(self):
        return self._urls

    @property
    def allow_urls(self):
        return self._allow_urls

class UrlFormatExtractor(BaseExtractor):

    def __init__(self,dom,response_url,page_rule,fid):
        self.__rule = page_rule
        self.__dom = dom
        self.__response_url = response_url

        args = page_rule.extract_url_element
        self._format_url = args.get('format_url')

        if not self._format_url:
            raise TypeError('format url配置中必须有format_url')

        #format_data中可以存在一些特殊的用法
        self._format_data = args.get('format_data')

        self._method = args.get('method','GET')
        self._data = args.get('data')
        self._headers = args.get('headers',None)
        self._cookies = args.get('cookies',None)

        self._fid = fid

        self._urls = []
        self._requests = []

        self._splice_urls()
        self._url2request()

    def __call__(self):
        return self._requests

    def _splice_urls(self):
        data_dict = {}

        if self._format_data:
            for key,formatter in self._format_data.items():
                #默认str为字符串
                if isinstance(formatter,(str,int)):
                    data_dict[key] = [formatter]
                elif isinstance(formatter,list):
                    data_dict[key] = formatter
                elif isinstance(formatter,dict):
                    dict_result = self._parse_formatter(formatter)
                    data_dict[key] = dict_result

        for format_data in self._yield_data(data_dict):
            #print self._format_url
            print format_data
            try:
                self._urls.append(self._format_url % format_data)
            except:
                raise TypeError('格式化url错误')
    
    def _yield_data(self,data_dict):
        product_data = []
        data_keys = data_dict.keys()

        for data_list in data_dict.values():
            product_data.append(data_list)

        for data in itertools.product(*product_data):
            yield_data_dict = {}

            for idx,key in enumerate(data_keys):
                yield_data_dict[key] = data[idx]

            yield yield_data_dict
              
    def _parse_formatter(self,formatter): 
        type = formatter.get('type','xpath')
        expression = formatter.get('expression')

        if not expression:
            raise TypeError('忘了写配置中的expression了')

        result = []

        if type == 'xpath':
            result = self.__dom.xpath(expression)
        elif type == 'css':
            result = self.__dom.cssselect(expression)

        return result

    def _url2request(self):
        request_args = {'method':self._method,'headers':self._headers,'cookies':self._cookies,'data':self._data,'fid':self._fid}

        for url in self._urls:
            request = REQ.Request(UTL.replenish_url(self.__response_url,url),rule_number = self.__rule.number+1,**request_args)
            self._requests.append(request)


class DataExtractor(BaseExtractor):
    
    def __init__(self,dom,page_rule,fid):
        self.__dom = dom
        self._extract_data_elements = page_rule.scrawl_data_element

        self._data = None
        self._fid = fid

        self._extract_data()

    def __call__(self,type = None):
        return self._data

    def _extract_data(self):
        results = {}

        for element in self._extract_data_elements:
            type = element.get('type','xpath')
            expression = element.get('expression')

            if not expression:
                raise TypeError('忘了写配置中的expression了')

            field = element.get('field')

            if not field:
                raise TypeError('忘了写配置中的field了')

            result = []

            if type == 'xpath':
                result = self.__dom.xpath(expression)
            elif type == 'css':
                result = self.__dom.cssselect(expression)

            results[field] = result

        self._results2data(results)
           
    def _results2data(self,results):
        self._data = DT.Data(**results)
        self._data.fid = self._fid

    @property
    def fid(self):
        return self._fid

def response2dom(response):
    try:
        dom = lxml.html.fromstring(response.content)
    except UnicodeDecodeError:
        dom = lxml.html.soupparser.fromstring(response.content)

    return dom




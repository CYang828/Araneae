#*-*coding:utf8*-*

import re

from Araneae.utils.setting import Setting

#0:没有,1:抽取url,2:格式化
NONE_URL_TYPE = 0
EXTRACT_URL_TYPE = 1
FORMAT_URL_TYPE = 2

class PageRule(object):
    """
    页面规则
    """
    __scrawl_url_type = NONE_URL_TYPE
    __scrawl_url_element = None
    __scrawl_data_element = None
    __scrawl_data_field = ''
    
    def __init__(self,map):
        self._essential(map)

    def _essential(self,map):
        if 'extract_urls' in map.keys():
            self.__scrawl_url_type = EXTRACT_URL_TYPE
            self.__scrawl_url_element = map['extract_urls']
        elif 'format_urls' in map.keys():
            self.__scrawl_url_type  = FORMAT_URL_TYPE
            self.__scrawl_url_element = map['format_urls']

        if 'extract_data' in map.keys():
            self.__scrawl_data_field = map['extract_data']['field']
            self.__scrawl_data_element ={'type':map['extract_data']['type'],'expression':map['extract_data']['type']}

    def scrawl_url(self):
        return (self.__scrawl_url_type,self.__scrawl_url_element)

    def scrawl_data(self):
        return (self.__scrawl_data_element,self.__scrawl_data_field)

    @property
    def field(self):
        return self.__scrawl_data_field

class BaseChromesome(Setting):
    """
    每个chromesome必须存在spider_name和first_url
    """
    def __init__(self,chromesome):

        self._attributes = chromesome._attributes
        self._essential_set()
        self._set_essential_options()

    @property
    def spider_name(self):
        return self['SPIDER_NAME']

    @property
    def first_url(self):
        return self['FIRST_URLS']

    @property
    def running_type(self):
        return self['RUNNING_TYPE']

    @property
    def scheduler(self):
        return self['SCHEDULER']

    def _essential_set(self):
        """
        必有参数
        """
        self.set_essential_keys('SPIDER_NAME','FIRST_URLS','RUNNING_TYPE','SCHEDULER')

    def _set_essential_options(self):
        """
        设置配置选项
        """
        self.set_options('RUNNING_TYPE','singleton','distributed')
        self.set_options('SCHEDULER','singleton','redis','rabbitmq')
    
class RuleLinkChromesome(BaseChromesome):
    __lasting = None
    __page_rules = []
    __essential_page_keys = set([])
    __page_exp = re.compile(r'PAGE(\d+)')
    __essential_keys = set(['SPIDER_NAME','FIRST_URLS'])

    def __init__(self,chromesome):
        super(RuleLinkChromesome,self).__init__(chromesome)
        self._essential()

    def _essential(self):
        for key in self.__essential_keys:
            if key not in self.keys():
                raise KeyError(key)

        self._sort_page()
        self.__lasting = self.get('LASTING',None)

    def _sort_page(self):
        page_sort_tmp = {}
        
        for key in self._attributes.keys():
            page_match = self.__page_exp.match(key)
 
            if page_match:
                page_num = page_match.group(1)
                page_sort_tmp[page_num] = key

        page_sort_tmp = sorted(page_sort_tmp.iteritems(),key = lambda i:i[0])

        self.__page_rules = [PageRule(self._attributes[sort_tmp_item[1]]) for sort_tmp_item in page_sort_tmp]

    def iter_page_rule(self):
        for page_rule in self.__page_rules:
            yield page_rule

    def get_page_rule(self,number):
        return self.__page_rules[number]

    @property
    def lasting(self):
        return self._lasting
        
class BroadPriorityChromesome(BaseChromesome):

    def __init__(self,chromesome):
        pass

class DeepPriorityChromesome(Setting):

    def __init__(self,chromesome):
        pass


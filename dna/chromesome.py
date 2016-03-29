#*-*coding:utf8*-*

import re

from Araneae.dna.rule import PageRule
from Araneae.utils.setting import Setting

RUNNING_TYPE_SINGLETON = 1
RUNNING_TYPE_DISTRIBUTED = 2

SCHEDULER_SINGLETON = 'SingletonScheduler'
SCHEDULER_REDIS = 'RedisScheduler'
SCHEDULER_RABBITMQ = 'RabbitMqScheduler'

class BaseChromesome(Setting):
    """
    每个chromesome必须存在spider_name和first_url
    """
    OPTIONS = {
                'RUNNING_TYPE':{'singleton':RUNNING_TYPE_SINGLETON,'distributed':RUNNING_TYPE_DISTRIBUTED},
                'SCHEDULER'  :{'singleton':SCHEDULER_SINGLETON,'redis':SCHEDULER_REDIS,'rabbitmq':SCHEDULER_RABBITMQ},
              }

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
        return self.OPTIONS['RUNNING_TYPE'][self['RUNNING_TYPE']]

    @property
    def scheduler(self):
        return self.OPTIONS['SCHEDULER'][self['SCHEDULER']]

    def _essential_set(self):
        """
        必有参数
        """
        self.set_essential_keys('SPIDER_NAME','FIRST_URLS','CONCURRENT_REQUESTS','RUNNING_TYPE','SCHEDULER')

    def _set_essential_options(self):
        """
        设置配置选项
        """
        for key,opt_info in self.OPTIONS.items():
            self.set_options(key,*opt_info.keys())
    
class RuleLinkChromesome(BaseChromesome):
    """
    链式爬虫
    """
    __lasting = None
    __page_rules = []
    __essential_page_keys = set([])
    __page_exp = re.compile(r'PAGE(\d+)')

    def __init__(self,chromesome):
        super(RuleLinkChromesome,self).__init__(chromesome)
        self._essential()

    def iter_page_rule(self):
        for page_rule in self.__page_rules:
            yield page_rule

    def get_page_rule(self,number):
        return self.__page_rules[number]

    def len(self):
        return len(self.__page_rules)

    @property
    def lasting(self):
        return self.__lasting
 
    def _essential(self):
        self._sort_page()
        self.__lasting = self.get('LASTING',None)

        if not self.len():
            raise TypeError('链路爬虫必须规定页面规则')

    def _sort_page(self):
        page_sort_tmp = {}
        
        for key in self._attributes.keys():
            page_match = self.__page_exp.match(key)
 
            if page_match:
                page_num = page_match.group(1)
                page_sort_tmp[page_num] = key

        page_sort_tmp = sorted(page_sort_tmp.iteritems(),key = lambda i:i[0])

        self.__page_rules = [PageRule(self._attributes[sort_tmp_item[1]]) for sort_tmp_item in page_sort_tmp]

       
class BroadPriorityChromesome(BaseChromesome):

    def __init__(self,chromesome):
        pass

class DeepPriorityChromesome(BaseChromesome):

    def __init__(self,chromesome):
        pass


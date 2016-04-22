#*-*coding:utf8*-*

import re
import collections

import Araneae.dna.rule as PR
import Araneae.utils.setting as SET

RUNNING_TYPE_SINGLETON = 1
RUNNING_TYPE_DISTRIBUTED = 2

SCHEDULER_SINGLETON = 'SingletonScheduler'
SCHEDULER_REDIS = 'RedisScheduler'
SCHEDULER_RABBITMQ = 'RabbitMqScheduler'

class BaseChromesome(SET.Setting):
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
    def first_urls(self):
        first_urls = self['FIRST_URLS']

        if isinstance(first_urls,str):
            self.set_from_value('FISRT_URLS',[first_urls])

        return self['FIRST_URLS']

    @property
    def running_type(self):
        return self.OPTIONS['RUNNING_TYPE'][self['RUNNING_TYPE']]

    @property
    def scheduler(self):
        return self.OPTIONS['SCHEDULER'][self['SCHEDULER']]

    @property
    def scheduler_retry_time(self):
        return self['SCHEDULER_RETRY_TIME']

    @property
    def merge_data_collection(self):
        return self['MERGE_DATA_COLLECTION']

    @property
    def middle_data_collection(self):
        return self['MIDDLE_DATA_COLLECTION']

    def _essential_set(self):
        """
        必有参数
        """
        self.set_essential_keys('SPIDER_NAME','FIRST_URLS','CONCURRENT_REQUESTS','RUNNING_TYPE','SCHEDULER','SCHEDULER_RETRY_TIME')

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
    __page_rules = collections.OrderedDict()
    __essential_page_keys = set([])
    __page_exp = re.compile(r'PAGE(\d+)')

    def __init__(self,chromesome):
        super(RuleLinkChromesome,self).__init__(chromesome)
        self._essential()

    def iter_page_rule(self):
        for rule_number,page_rule in self.__page_rules.items():
            yield page_rule

    def get_page_rule(self,number):
        return self.__page_rules[number] if number in self.__page_rules.keys() else None

    def __len__(self):
        return len(self.__page_rules)

    @property
    def first_rule_number(self):
        return  min(self.__page_rules.keys())

    @property
    def lasting(self):
        return self.__lasting
 
    def _essential(self):
        self._sort_page()
        self.__lasting = self.get('LASTING',None)

        if not len(self):
            raise TypeError('链路爬虫必须规定页面规则')

    def _sort_page(self):
        page_sort_tmp = {}
        
        for key in self._attributes.keys():
            page_match = self.__page_exp.match(key)
 
            if page_match:
                page_num = int(page_match.group(1))
                page_sort_tmp[page_num] = key


        page_sort_tmp = {rule_number:PR.PageRule(self._attributes[sort_tmp_item]).set_number(rule_number) for rule_number,sort_tmp_item in page_sort_tmp.items()}
        self.__page_rules = collections.OrderedDict(sorted(page_sort_tmp.items(),key = lambda i:i[0]))

        first_flag = True
        upper_page_rule = None

        for rule_number,page_rule in self.__page_rules.items():
            if first_flag:
                first_flag = False
                upper_page_rule = page_rule
                continue
            
            upper_page_rule.next_number = page_rule.number
            upper_page_rule = page_rule
            
        
        """
        for rule_number,rule in enumerate(self.__page_rules):
            rule.number = rule_number
        """
       
class BroadPriorityChromesome(BaseChromesome):

    def __init__(self,chromesome):
        pass

class DeepPriorityChromesome(BaseChromesome):

    def __init__(self,chromesome):
        pass


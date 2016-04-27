#*-*coding:utf8*-*

import re
import collections

import Araneae.dna.rule as PR
import Araneae.utils.setting as SET
import Araneae.man.exception as EXP

RUNNING_TYPE_SINGLETON = 1
RUNNING_TYPE_DISTRIBUTED = 2

SCHEDULER_SINGLETON = 'SingletonScheduler'
SCHEDULER_REDIS = 'RedisScheduler'
SCHEDULER_RABBITMQ = 'RabbitMqScheduler'

SPIDER_TYPE_RUlELINK = 'RuleLink'

DEFAULT_RUNNING_TYPE = SCHEDULER_SINGLETON
DEFAULT_SCHEDULER = SCHEDULER_SINGLETON
DEFAULT_SCHEDULER_RETRY_TIME = 2 
DEFAULT_SCHEDULER_RETRY_INTERVAL = 5
DEFAULT_CONCURRENT_REQUESTS = 5
DEFAULT_REQUEST_SLEEP_TIME = 0
DEFAULT_REQUEST_TIMEOUT = 2
DEFAULT_MIDDLE_DATA_COLLECTION = 'rule'
DEFAULT_MERGE_DATA_COLLECTION = 'merge_result'
DEFAULT_USER_AGENT = True
DEFAULT_HTTP_PROXY = False


class BaseChromesome(SET.Setting):
    """
    chromesome基类
    """
    #可选项配置
    OPTIONS = {
                'RUNNING_TYPE':{'singleton':RUNNING_TYPE_SINGLETON,'distributed':RUNNING_TYPE_DISTRIBUTED},
                'SCHEDULER'   :{'singleton':SCHEDULER_SINGLETON,'redis':SCHEDULER_REDIS,'rabbitmq':SCHEDULER_RABBITMQ},
              }

    def __init__(self,chromesome):
        self._attributes = chromesome._attributes
        self._essential_set()
        self._set_essential_options()

    def _essential_set(self):
        #self.set_essential_keys('LOG_PATH','LOG_FORMAT','LOG_LEVEL','LOG_DATE_FORMAT')
        self.set_essential_keys('RUNNING_TYPE')
        self.set_essential_keys('USER_AGENT','HTTP_PROXY','HTTP_PROXY_MODULE')
        self.set_essential_keys('SCHEDULER','SCHEDULER_RETRY_TIME','SCHEDULER_RETRY_INTERVAL')
        self.set_essential_keys('CONCURRENT_REQUESTS','REQUEST_SLEEP_TIME','REQUEST_TIMEOUT')
        self.set_essential_keys('MIDDLE_DATA_COLLECTION','MERGE_DATA_COLLECTION','LASTING')
        self.set_essential_keys('SPIDER_NAME','SPIDER_TYPE','FIRST_URLS','LOGIN_HEADER')
        self.set_essential_keys('REQUEST_MIDDLEWARE','DATA_MIDDLEWARE','FILE_MIDDLEWARE')

    def _set_essential_options(self):
        for key,opt_info in self.OPTIONS.items():
            self.set_options(key,*opt_info.keys())

    @property
    def user_agent(self):
        return  self.getbool('USER_AGENT',DEFAULT_USER_AGENT)

    @property
    def http_proxy(self):
        return  self.getbool('HTTP_PROXY',DEFAULT_HTTP_PROXY)

    @property
    def http_proxy_module(self):
        return self.getbool('HTTP_PROXY_MODULE',None)

    @property
    def running_type(self):
        return self.OPTIONS['RUNNING_TYPE'][self.get('RUNNING_TYPE',DEFAULT_RUNNING_TYPE)]

    @property
    def scheduler(self):
        return self.OPTIONS['SCHEDULER'][self.get('SCHEDULER',DEFAULT_SCHEDULER)]

    @property
    def scheduler_retry_time(self):
        return self.getint('SCHEDULER_RETRY_TIME',DEFAULT_SCHEDULER_RETRY_TIME)

    @property
    def scheduler_retry_interval(self):
        return self.getint('SCHEDULER_RETRY_INTERVAL',DEFAULT_SCHEDULER_RETRY_INTERVAL)

    @property
    def concurrent_requests(self):
        return self.getint('CONCURRENT_REQUESTS',DEFAULT_CONCURRENT_REQUESTS)

    @property
    def request_sleep_time(self):
        return self.getint('REQUEST_SLEEP_TIME',DEFAULT_REQUEST_SLEEP_TIME)

    @property
    def request_timeout(self):
        return self.getint('REQUEST_TIMEOUT',DEFAULT_REQUEST_TIMEOUT)

    @property
    def middle_data_collection(self):
        return self.get('MIDDLE_DATA_COLLECTION',DEFAULT_MIDDLE_DATA_COLLECTION)
   
    @property
    def merge_data_collection(self):
        return self.get('MERGE_DATA_COLLECTION',DEFAULT_MERGE_DATA_COLLECTION)

    @property
    def lasting(self):
        return self.getdict('LASTING',None)

    @property
    def spider_name(self):
        spider_name = self.get('SPIDER_NAME',None)

        if not spider_name:
            raise EXP.SettingException('爬虫SPIDER_NAME不能为空')

        return spider_name
        
    @property
    def spider_type(self):
        spider_type = self.get('SPIDER_TYPE',None)

        if not spider_type:
            raise EXP.ChromesomeException('爬虫SPIDER_TYPE不能为空')

        return spider_name

    @property
    def login_header(self):
        return self.getdict('LOGIN_HEADER',None)

    @property
    def first_urls(self):
        first_urls = self.get('FIRST_URLS',None)

        if not first_urls:
            raise EXP.ChromesomeException('爬虫FIRST_URLS不能为空')

        if isinstance(first_urls,str):
            self.set_from_value('FISRT_URLS',[first_urls])

        return self.getlist('FIRST_URLS')

    @property
    def request_middleware(self):
        return self.getlist('REQUEST_MIDDLEWARE')

    @property
    def data_middleware(self):
        return self.getlist('DATA_MIDDLEWARE')

    @property
    def file_middleware(self):
        return self.getlist('FILE_MIDDLEWARE')
   
   
 
class RuleLinkChromesome(BaseChromesome):
    """
    链式爬虫配置文件规则
    """
    _page_exp = re.compile(r'PAGE(\d+)')
    __page_rules = collections.OrderedDict()
    __essential_page_keys = set([])

    def __init__(self,chromesome):
        super(RuleLinkChromesome,self).__init__(chromesome)
        self._essential()

    def __len__(self):
        return len(self.__page_rules)

    def _essential(self):
        self._sort_page()

        if not len(self):
            raise EXP.ChromesomeException('RuleLink爬虫页面必须存在页面规则')

    def _sort_page(self):
        page_sort_tmp = {}
        
        for key in self._attributes.keys():
            page_match = self._page_exp.match(key)
 
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
 
    def iter_page_rule(self):
        for rule_number,page_rule in self.__page_rules.items():
            yield page_rule

    def get_page_rule(self,number):
        return self.__page_rules[number] if number in self.__page_rules.keys() else None

    @property
    def first_rule_number(self):
        return  min(self.__page_rules.keys())

    @property
    def first_rule(self):
        return self.__page_rules[self.first_rule_number]

       
class BroadPriorityChromesome(BaseChromesome):
    """
    广度优先爬虫配置文件规则
    """
    def __init__(self,chromesome):
        pass


class DeepPriorityChromesome(BaseChromesome):
    """
    深度优先爬虫配置文件规则
    """
    def __init__(self,chromesome):
        pass


#*-*coding:utf8*-*
"""
爬虫配置文件
============
"""
from collections import OrderedDict

#爬虫运行方式
#可选类型:singleton,distributed
RUNNING_TYPE = 'singleton'

#调度器
#调度器的类路径
SCHEDULER = 'Araneae.scheduler.RedisScheduler'
#调度器配置
SCHEDULER_CONF = {'host': '172.18.4.52', 'port': 6379, 'db': 8, 'password': None, 'timeout': 5, 'charset': 'utf8'}
#去重器
#去重器类路径
DUPEFILTER = 'Araneae.dupefilter.RedisDupeFilter'
#去重器配置
DUPEFILTER_CONF = {'host': '172.18.4.52', 'port': 6379, 'db': 8, 'password': None, 'timeout': 5, 'charset': 'utf8'}

#调度器重试次数
SCHEDULER_RETRY_TIME = 5
#调度器重试间隔,单位秒
SCHEDULER_RETRY_INTERVAL = 1

DOWNLOADER_PATH = '/image'

#爬虫最大并发数
CONCURRENT_REQUESTS = 1
#请求休眠时间,单位秒
REQUEST_SLEEP_TIME = 3
#请求超时时间,单位秒
REQUEST_TIMEOUT = 2

#日志路径,结尾必须为.log
LOG_PATH = '/home/zhangchunyang/log/jintaiyang_chuzhong.log'

#爬虫名
SPIDER_NAME = 'jintaiyang_chuzhong'
#爬虫类型
SPIDER_TYPE = 'rulelink'

#中间数据结果集前缀
MIDDLE_DATA_COLLECTION = 'rule'
#合并后结果集前缀
MERGE_DATA_COLLECTION = 'merge_result'
#持久化存储配置
LASTING = {'type': 'mongo', 'host': '172.18.4.52', 'port': '27017', 'password': '', 'timeout': 5}

#登录的headers
LOGIN_HEADER = {'Cookie': 'DWRSESSIONID=mAUMO8vo8Uvr1vbiRI68BZRt5kl; Hm_lvt_acbe332524305cf7430995bc4404a862=1464232093; JSESSIONID=abcFQNItJngAZbnPK9-tv; jsessionid=0AEA67AC6C8EF4A88A88EE69A41E2018'}

#爬虫初始地址
FIRST_URLS = [
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001002.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001003.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001004.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001005.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001006.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001007.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001008.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001009.shtm',
    'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001010.shtm',
]

#页面爬取规则
PAGE1 = {'extract_urls': {'allow': r'/Jty/tbkt/getTbkt2_currentBitCode_\d{12}.shtm', }}

PAGE2 = {'extract_urls': {'allow': r'/Jty/tbkt/getTbkt2_currentBitCode_\d{15}.shtm', }}
PAGE3 = {'extract_urls': {'allow': r'/Jty/tbkt/getTbkt2_currentBitCode_\d{18}.shtm', }}
PAGE4 = {'extract_urls': {'allow': r'/Jty/tbkt/getTbkt2.action\?currentBitCode=\d{21}', }}
PAGE5 = {
    'extract_urls':
    {
        'allow': r'/jty/tbkt/showDetail.action\?articleId=\d*',
    },
    'format_next_page':
    {
        'format_url': '%(url)s&pageSize=20&showPage=%(page)s',
        'format_data': OrderedDict([
            ('url', {'type': 'constant',
                     'expression': '@host_url'}), ('@pages', {'type': 'xpath',
                                                              'expression':
                                                              r'//*[@id="ddd"]/nobr/select[1]/option[@*]/text()'}
                                                   ), ('@max_page', {'type': 'function',
                                                                     'expression': 'max(@pages)'}), ('page', {'type': 'function',
                                                                                                              'expression': 'range(2,@max_page+1)'})
        ]),
    }
}
PAGE6 = {
    'extract_data':
    [
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[1]/tbody/tr/td/a[2]/text()',
            'field': 'subject',
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[1]/tbody/tr/td/a[3]/text()',
            'field': 'grade',
            'parent': 0,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[1]/tbody/tr/td/a[4]/text()',
            'field': 'publishing_house',
            'parent': 1,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[1]/tbody/tr/td/a[5]/text()',
            'field': 'unit',
            'parent': 2,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[1]/tbody/tr/td/a[6]/text()',
            'field': 'name',
            'parent': 3,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[1]/tbody/tr/td/a[7]/text()',
            'field': 'resource_type',
            'parent': 4,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[2]/tbody/tr[1]/td/div/text()',
            'field': 'title',
            'parent': 5,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[2]/tbody/tr[4]/td/div/text()',
            'field': 'description',
            'parent': 6,
            'mutiple': False
        },
        {
            'type': 'xpath',
            'expression':
            '//*[@id="mainContent"]/form/table[2]/tbody/tr[2]/td/div/text()',
            'field': 'resource_info',
            'parent': 7,
            'mutiple': False
        },
    ],
    'extract_files':
    {
        'allow': r'/jty/tbkt/downLoadAttach\.action\?articleId=\d*&urlId=1',
        'field': 'file'
    }
}

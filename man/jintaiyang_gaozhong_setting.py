#!*-*coding:utf8*-*

#调度器
#调度器的类路径
SCHEDULER = 'Araneae.scheduler.RedisScheduler'
#调度器配置
SCHEDULER_CONF = {'host': '172.18.4.52', 'port': 6379, 'db': 7, 'password': None, 'timeout': 5, 'charset': 'utf8'}

#去重器
#去重器类路径
DUPEFILTER = 'Araneae.dupefilter.RedisDupeFilter'
#去重器配置
DUPEFILTER_CONF = {'host': '172.18.4.52', 'port': 6379, 'db': 7, 'password': None, 'timeout': 5, 'charset': 'utf8'}

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
LOG_PATH = '/home/zhangchunyang/log/jintaiyang_gaozhong.log'

#爬虫名
SPIDER_NAME = 'jintaiyang_gaozhong'
#爬虫类型
SPIDER_TYPE = 'rulelink'

#中间数据结果集前缀
MIDDLE_DATA_COLLECTION = 'rule'
#合并后结果集前缀
MERGE_DATA_COLLECTION = 'merge_result'
#持久化存储配置
LASTING = {'type': 'mongo', 'host': '172.18.4.52', 'port': '27017', 'password': '', 'timeout': 5}

#登录的headers
#LOGIN_HEADER = {}

#爬虫初始地址
FIRST_URLS = ['http://www.jtyhjy.com/zyw/synclass/home#1']

PAGE1 = {   
            'extract_data':
            {
                #'type':'css',
                #'expression':'#course > a.z-sel',
                'type':'xpath',
                'expression':'//*[@id="course"]/a/text()',
                'field':'course',
                'multiple':True,
                'associate':True
            },

            'extract_urls': 
            {
                'allow': r'^synclass/c\d{4}$'
            }
        }

PAGE2 = {
            'extract_data':
            {   
                #'type':'css',
                #'expression':'#version > a.z-sel',
                'type':'xpath',
                'expression':'//*[@id="version"]/a/text()',
                'field':'version',
                'multiple':True,
                'associate':True       
            },

            'extract_urls': 
            {
                'allow': r'^synclass/c\d{4}_v\d+$'
            }
        }

PAGE3 = {
            'extract_data':
            {   
                #'type':'css',
                #'expression':'#version > a.z-sel',
                'type':'xpath',
                'expression':'//*[@id="module"]/a/text()',
                'field':'module',
                'multiple':True,
                'associate':True       
            },

            'extract_urls': 
            {
                'allow': r'^synclass/c\d{4}_v\d+_m\d+$'
            }
        }

PAGE4 = {
            'extract_data':
            [
                {
                'type' : 'group_xpath',
                'group_expression' : '//*[@id="m-bottom"]/div/div[1]/',
                'expression' : ['div[*]/h3/a/text()', 'div[?0]/a/text()'],
                'field': ['unit', 'lession'],
                'multiple': True,
                'associate': False
                }
            ]
        }

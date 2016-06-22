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
LOG_PATH = '/home/zhangchunyang/log/xdf_gongkaike.log'

#爬虫名
SPIDER_NAME = 'xdf_gongkaike'
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
FIRST_URLS = ['http://v.koolearn.com/c/2191-0.html']

PAGE1 = {   
            'extract_urls': 
            {
                'allow': r'^http://v.koolearn\.com/\d{8}/\d{4}\.html$'
            },
            'format_next_page': 
            {
                'format_url':'http://cmsapp.koolearn.com/gongkaike.php?a=catlist_page&catid=2191&ord=1&page_num=%(page_num)d&callback=jsonp1464861512911',
                'format_data':{
                                    'page_num':{'type':'function','expression':'range(1,20)'},
                              }
            }
        }

PAGE2 = {
            'extract_data':
            [
                {
                    'type': 'xpath',
                    'expression':'/html/body/div[5]/div[2]/p/a[3]',
                    'field': 'stage',#学段
                    'mutiple': False  
                },
                {
                    'type': 'xpath',
                    'expression':'/html/body/div[5]/h4',
                    'field': 'title',#标题
                    'parent':0,
                    'mutiple': False  
                },
                {
                    'type': 'xpath',
                    'expression':'/html/body/div[5]/div[5]/div[2]/div[1]/p[2]',
                    'field': 'create_time',#创建时间
                    'parent':1,
                    'mutiple': False  
                },
                {
                    'type': 'xpath',
                    'expression':'/html/body/div[5]/div[5]/div[2]/div[1]/p[5]',
                    'field': 'long',#时长
                    'parent':2,
                    'mutiple': False  
                },
                {
                    'type': 'xpath',
                    'expression':'/html/body/div[5]/div[5]/div[2]/div[1]/p[6]',
                    'field': 'description',#描述
                    'parent':3,
                    'mutiple': False  
                },
            ],

            'format_files':
            {
                'format_url':'%(dir_mp4)s',
                'format_data':{
                                'dir_mp4':{'type':'xpath','expression':'/html/body/div[5]/div[3]/div/div[1]/@dir_mp4'}
                              },
                'field':'video'
            }
        }


#*-*coding:utf8*-*
"""
爬虫默认配置文件
"""

##整个系统配置
#爬虫运行方式
#可选类型:singleton,distributed
#如果是distributed,需要通过发现服务发现其他服务器
RUNNING_TYPE = 'singleton'

##调度器配置
#调度器的类路径
SCHEDULER = 'Araneae.scheduler.MemoryScheduler'
#调度器配置
SCHEDULER_CONF = {}
#调度器重试次数
SCHEDULER_RETRY_TIME = 5
#调度器重试间隔,单位秒
SCHEDULER_RETRY_INTERVAL = 1

##去重器配置
#去重器类路径
DUPEFILTER = 'Araneae.dupefilter.MemoryDupeFilter'
#去重器配置
DUPEFILTER_CONF = {}

##下载器配置
#下载器类路径
DOWNLOADER = 'Araneae.downloader.WorkerDownloader'
#下载文件存储路径
DOWNLOADER_PATH = ''

##数据管道配置
#中间数据结果集前缀
MIDDLE_DATA_COLLECTION = 'rule'
#合并后结果集前缀
MERGE_DATA_COLLECTION = 'merge_result'
#持久化存储配置
LASTING = {}

##爬虫网络配置
#爬虫最大并发数
CONCURRENT_REQUESTS = 1
#请求休眠时间,单位秒
REQUEST_SLEEP_TIME = 2
#请求超时时间,单位秒
REQUEST_TIMEOUT = 2
#请求重试次数
REQUEST_RETRY_TIME = 3

#随机获取user agent
USER_AGENT = True
#随机获取proxy列表中ip
HTTP_PROXY = False
#proxy列表模块地址,键名为PROXY_IP
HTTP_PROXY_MODULE = ''

#日志路径
LOG_PATH = ''

#爬虫名
SPIDER_NAME = ''
#爬虫类型
#可选类型:rulelink
SPIDER_TYPE = ''
#登录的headers
LOGIN_HEADER = {}
#爬虫初始地址
FIRST_URLS = []
#request中间件
REQUEST_MIDDLEWARE = ['Araneae.middleware.UserAgentMiddleware']
#data中间件
DATA_MIDDLEWARE = []
#file中间件
FILE_MIDDLEWARE = []

##页面爬去规则
#PAGE + 数字编号,爬去会按照编号的的从小到大的顺序进行爬去

#*-*coding:utf8*-*

"""
爬虫配置文件
============
"""
#爬虫运行方式
#可选类型:singleton,distributed
#此选项是针对整个系统的
#如果是distributed,需要多台机器的信息
RUNNING_TYPE = 'singleton'

#调度器类型
#可选类型:singleton,redis,rabbitmq
SCHEDULER = 'singleton'
#调度器重试次数
SCHEDULER_RETRY_TIME = 5
#调度器重试间隔,单位秒
SCHEDULER_RETRY_INTERVAL = 1


#爬虫最大并发数
CONCURRENT_REQUESTS = 1
#请求休眠时间,单位秒
REQUEST_SLEEP_TIME = 2
#请求超时时间,单位秒
REQUEST_TIMEOUT = 2
#请求重试次数
REQUEST_RETRY_TIME = 3

#中间数据结果集前缀
MIDDLE_DATA_COLLECTION = 'rule'
#合并后结果集前缀
MERGE_DATA_COLLECTION = 'merge_result'
#持久化存储配置
LASTING         =   {}


#随机获取user agent
USER_AGENT = True
#随机获取proxy列表中ip
HTTP_PROXY = False
#proxy列表模块地址,键名为PROXY_IP
HTTP_PROXY_MODULE = None

#日志路径
LOG_PATH = None

#爬虫名
SPIDER_NAME     =   None
#爬虫类型
#可选类型:rulelink
SPIDER_TYPE     =   None
#登录的headers
LOGIN_HEADER = {}
#爬虫初始地址
FIRST_URLS       =   []
#request中间件
REQUEST_MIDDLEWARE = ['Araneae.middleware.UserAgentMiddleware']
#data中间件
DATA_MIDDLEWARE = []
#file中间件
FILE_MIDDLEWARE = []


"""
页面爬去规则
PAGE + 数字编号,爬去会按照编号的的从小到大的顺序进行爬去
"""

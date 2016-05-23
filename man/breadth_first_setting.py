#*-*coding:utf8*-*

"""
爬虫配置文件
============
"""
#爬虫运行方式
#可选类型:singleton,distributed
RUNNING_TYPE = 'singleton'

#调度器类型
#可选类型:singleton,redis,rabbitmq
#调度器的类路径
SCHEDULER = 'Araneae.scheduler.RedisScheduler'

#调度器配置
SCHEDULER_CONF = {
                    'host':'localhost',
                    'port':6379,
                    'db':0,
                    'password':None,
                    'timeout':5,
                    'charset':'utf8'
                 }

#去重器类路径
DUPEFILTER = 'Araneae.dupefilter.RedisDupeFilter'

#去重器配置
DUPEFILTER_CONF= {
                    'host':'localhost',
                    'port':6379,
                    'db':0,
                    'password':None,
                    'timeout':5,
                    'charset':'utf8'
                }

#调度器重试次数
SCHEDULER_RETRY_TIME = 5

#调度器重试间隔,单位秒
SCHEDULER_RETRY_INTERVAL = 2

#爬虫最大并发数
CONCURRENT_REQUESTS = 1

#请求休眠时间,单位秒
REQUEST_SLEEP_TIME = 1

#请求超时时间,单位秒
REQUEST_TIMEOUT = 2

#日志路径,结尾必须为.log
LOG_PATH = '/home/guoweijiang/Araneae/dna/spider.log'

#下载文件存储目录
DOWNLOAD_PATH = '/home/guoweijiang/download/%s/'

#爬虫名
SPIDER_NAME = 'bfspider'

#爬虫类型
SPIDER_TYPE = 'breadthfirst'

#中间数据结果集前缀
MIDDLE_DATA_COLLECTION = 'breadth_first_'

#合并后结果集前缀
MERGE_DATA_COLLECTION = 'merge_result'

#  持久化存储配置
LASTING = {
           'type':'mongo_tree',
           'host':'localhost',
           'port':'27017',
           'password':'',
           'timeout':5
          }

MASTER_CONF = {
                'host':'10.60.0.165',
                'port':'',
                'password':'',
                'db':0,
                'timeout':5,
              }

# 登录的headers
# TODO 如果爬取的过程时间过长，会不会出现 cookie 过期的现象。 目前没法动态获取合法 cookie。重新启动爬虫如何保证不重复
LOGIN_HEADER = {'DWRSESSIONID':'nI68mNQi5qXP0aN680MnpzARcjl','JSESSIONID':'abcLQ55WxX8DfaJYdemtv'}

#爬虫初始地址
# FIRST_URLS = ['http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm']
FIRST_URLS = ['http://czy.jtyhjy.com/jty/tbkt/showDetail.action?articleId=3748556']
# FIRST_URLS = ['http://czy.jtyhjy.com/jty/tbkt/showDetail.action?articleId=3797907']

#  最终页面爬取规则为，遍历找到 download 页面，并下载相应资源
PAGE_RULE = \
{
    #  通过 value 替换生成最终 url      ObjectId("573974d19e34fd085dfa359d")
    'substitute_urls' :
    {
        #  html 中出现  javascript:pageSubmit 生成 url
        'javascript:pageSubmit' :
        {
            #  [@X] 表示通过 extract_regular 正则表达式从 javascript:pageSubmit 函数内容中取出的第 X 个参数。[0,N)
            #  [$X] 表示通过 xpath 从 DOM 中获取值，X 表示 'extract_xpath' 数组的索引。
            'format_url' : '/Jty/tbkt/getTbkt2.action?currentBitCode=[@1]&pageSize=[$0]&showPage=[@0]',
            'extract_regular' : '''[\\'\\"]([^\\'\\"]+?)[\\'\\"]''',
            'extract_xpath' : ['//select[@name=\'pageSize\']/option[@selected]/text()']
        }

        #  ... 可能还有别的替换模式
    },

    #  html 内容过滤器
    'content_filter' :
    {
        #  忽略抓取的 url
        'deny_urls': ['.*?getTbkt_currentBitCode_[\d]{6}.shtm'],

        #  允许抓取的 url         例：只抓取【七年级语文】
        'valid_urls' : ['.*?currentBitCode_001001001[\d]*?.shtm',
                         '.*?jty/tbkt/showDetail.action.*'],

        #  有时候只凭 title 会遗漏
        'valid_titles' : ['七年级']
    },

    #  最终叶子页面的模式匹配
    'leaf_page' :
    {
        #  需要找到一个标记，能够唯一标识叶子页面。通过正则匹配
        #  document.title=' 第一单元综合测试卷二 苏教版七年级语文下册';
        'leaf_flag' : 'document.title=',

        'leaf_extract_regular' :
        {
            #  叶子节点路径名，即所有祖先的名称
            'leaf_route_path_extract' : ['//div[@id="mainContent"]/table[1]/tbody/tr/td/a[normalize-space(text())!=""]/text()',
                                            '//div[@id="mainContent"]/form/table[1]/tbody/tr/td/a[normalize-space(text())!=""]/text()'],

            #  下载文件路径
            'leaf_download_extract' : '//div[@id="mainContent"]/form/table[2]/tbody/tr[3]/td[1]/table/tbody/tr/td/a//@href'
        }
    }
}


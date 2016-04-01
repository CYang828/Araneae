#*-*coding:utf8*-*

SPIDER_TYPE     =   'RuleLink'
SPIDER_NAME     =   'demo'
FIRST_URLS       =   ['http://news.sina.com.cn/']
LASTING         =   {
                        'type':'mongo',
                        'host':'10.60.0.65',
                        'port':'27017',
                        'password':'',
                        'db':'',
                        'timeout':5
                    }
PAGE1           =   {
                        'extract_urls':
                        {
                            'allow':r'http://news.sina.com.cn/c',
                            'deny':r'http://news.sina.com.cn/china/',
                            'headers':{'name':'zhangchunyang'},
                            'cookies':{'user':'zhangchunyang'},#如果不指定，沿用上一页后的http头
                            'method':'GET',
                            #'body':
                        },
                        'format_urls':
                        {
                            'type':'',
                            'format':'',
                            'data':{},
                            'method':''
                        },
                        'extract_data':
                        {
                            'type':'', #reg #xpath
                            'expression':'',
                            'field':'school_name'
                        },
                    }

#PAGE2 = {'name':'li'}

SCHEDULER = 'singleton'
RUNNING_TYPE = 'singleton'
CONCURRENT_REQUESTS = 10
SCHEDULER_RETRY_TIME = 5
SCHEDULER_RETRY_INTERVAL = 1
REQUEST_TIMEOUT = 2#还未添加

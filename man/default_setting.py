#*-*coding:utf8*-*

SPIDER_TYPE     =   'RuleLink'
SPIDER_NAME     =   'demo'
FIRST_URLS       =   ['http://www.baidu.com','http://blog.csdn.net/handsomekang/article/details/40889703','http://anandology.com/python-practice-book/iterators.html','http://stackoverflow.com/questions/6416538/how-to-check-if-an-object-is-a-generator-object-in-python']
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
                            'allow':'d',
                            'deny':'d',
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

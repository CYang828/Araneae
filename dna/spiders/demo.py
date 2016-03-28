SPIDER_TYPE     =   'RuleLink'
SPIDER_NAME     =   'demo'
FIRST_URLS       =   ['http://www.baidu.com','http://blog.csdn.net/handsomekang/article/details/40889703','http://anandology.com/python-practice-book/iterators.html','http://stackoverflow.com/questions/6416538/how-to-check-if-an-object-is-a-generator-object-in-python']
LASTING         =   {
                        'type':'',
                        'host':'',
                        'port':'',
                        'password':'',
                        'db':''
                    }
PAGE1           =   {
                        'extract_urls':
                        {
                            'allow':'',
                            'deny':''
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
                            'field':''
                        },
                    }

PAGE2 = {'name':'li'}

SCHEDULER = 'SingletonScheduler'
RUNNING_TYPE = 'singleton'

#*-*coding:utf8*-*

"""
爬虫配置文件
============
"""
from collections import OrderedDict


#爬虫运行方式
#可选类型:singleton,distributed
RUNNING_TYPE = 'singleton'


#调度器类型
#可选类型:singleton,redis,rabbitmq
SCHEDULER = 'redis'
#调度器重试次数
SCHEDULER_RETRY_TIME = 5
#调度器重试间隔,单位秒
SCHEDULER_RETRY_INTERVAL = 1


#爬虫最大并发数
CONCURRENT_REQUESTS = 1
#请求休眠时间,单位秒
REQUEST_SLEEP_TIME = 3
#请求超时时间,单位秒
REQUEST_TIMEOUT = 2

#日志路径,结尾必须为.log
LOG_PATH = '/home/zhangchunyang/log/spider.log'

#爬虫名
SPIDER_NAME     =   'jintaiyang_chuzhong'
#爬虫类型
SPIDER_TYPE     =   'rulelink'


#中间数据结果集前缀
MIDDLE_DATA_COLLECTION = 'rule'
#合并后结果集前缀
MERGE_DATA_COLLECTION = 'merge_result'
#持久化存储配置
LASTING         =   {
                        'type':'mongo',
                        'host':'172.18.4.52',
                        'port':'27017',
                        'password':'',
                        'timeout':5
                    }


#登录的headers
LOGIN_HEADER = {'Cookie':'DWRSESSIONID=JIvEqVolOFF8u2H2XTxcG4LJ5il; JSESSIONID=abcE071wq2xkD_FDBT-rv; jsessionid=D3E2ACF771A9E3D050E97A1F4D09F39F'}

#爬虫初始地址
FIRST_URLS       =   ['http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm']

#页面爬取规则
PAGE1           =   {
                        'extract_urls':
                        {
                            'allow':r'/Jty/tbkt/getTbkt2_currentBitCode_\d{12}.shtm',
                        }
                    }

PAGE2           =   {
                        'extract_urls':
                        {           
                            'allow':r'/Jty/tbkt/getTbkt2_currentBitCode_\d{15}.shtm',
                        }
                    }
PAGE3           =   {
                       'extract_urls':
                       {
                           'allow':r'/Jty/tbkt/getTbkt2_currentBitCode_\d{18}.shtm',
                       }
                    }
PAGE4           =   {
                        'extract_urls':
                        {
                            'allow':r'/Jty/tbkt/getTbkt2.action?currentBitCode=\d{21}',
                        }
                    }
PAGE5           =   {
                        'extract_urls':
                        {
                            'allow':r'/jty/tbkt/showDetail.action?articleId=\d*',
                        },
                        'format_next_page':
                        {
                            'format_url':'%(url)s&pageSize=20&showPage=%(page)s',
                            'format_data':OrderedDict([
                                            ('url',{'type':'constant','expression':'@host_url'}),
                                            ('@pages',{'type':'xpath','expression':'//*[@id="ddd"]/nobr/select[1]/option[*]/text()'}),
											('@max_page',{'type':'function','expression':'max(@pages)'}),
											('page',{'type':'function','expression':'range(2,@max_page+1)'})
                                          ]),
                        }
                    }
PAGE6           =   {
                        'extract_data':
                        {
                            'type':'xpath',
                            'expression':'//*[@id="mainContent"]/table[1]/tbody/tr/td/text()'
                        },
                        'extract_files':
                        {
                            'allow':r'/jty/tbkt/downLoadAttach\.action\?articleId=\d*',
                            'field':'file'
                        }
                    }
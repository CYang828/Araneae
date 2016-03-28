#*-*coding:utf8*-*
import types
import Araneae.scheduler
from data import Data
from gevent.pool import Pool
from Araneae.net.request import Request
from Araneae.db import generate_pipeline
from chromesome import BaseChromesome

"""
`spider.py` -- 爬虫组件
=======================
"""

DEFAULT_SCHEDULER = 'SingletonScheduler'
DEFAULT_RUNNING_TYPE = 'Singleton'
DEFAULT_MAX_POOL_LENGTH = 10

class BaseSpider(object):
    """
    每个spider必备:
        +一个scheduler,用来pull任务
        +一个chromesome,配置爬去规则
        +一个pool,用来爬取任务,pool的大小可以限制爬虫的速度
        +一个name,用来唯一标识一个爬虫
        +一个thread_id,每个爬虫都在一个thread中
        +一个data_pipeline,一个传输数据管道,根据配置爬虫情况(可选)
        +一个rpc对象,如果为单机模式,rpc关联到scheduler进行push,单机模式下功能退化,只能满足简单的爬虫功能(rpc对象必须有一个和scheduler相同的push接口)
        +运行类型:#Singleton单机模式(默认为该模式),Distributed(分布式,需要启动master,所有功能都能使用)
    """
    __rpc = None
    __name = ''
    __pool = None
    __thread_id = 0
    __scheduler = None
    __chromesome = None
    __running_type = ''     
    __data_pipeline = None

    def __init__(self,chromesome):
        """
        初始化spider必要参数

        """
        if isinstance(chromesome,BaseChromesome):
            self.__chromesome = chromesome
        else:
            raise TypeError('参数必须为Chromesome类型')

        self.__name = chromesome.get('SPIDER_NAME')
        self.__running_type = chromesome.get('RUNNING_TYPE',DEFAULT_RUNNING_TYPE)
        self.__pool = Pool(chromesome.get('MAX_POOL_LENGTH',DEFAULT_MAX_POOL_LENGTH))
        self.__scheduler = getattr(Araneae.scheduler,chromesome.get('SCHEDULER'),DEFAULT_SCHEDULER)()
        
        if chromesome.lasting:
            self.__data_pipeline = generate_pipeline(chromesome.lasting)

    def fetch_sync(self,request,callback = None):
        """
        阻塞访问request,用于必须确保完成的任务
        """
        self.fetch(request,callback = callback)
        self._join()

    def fetch(self,request,callback = None):
        """
        异步访问request
        """
        self.__pool.spawn(self._fetch,request,callback)
    
    def first_url(self,first_urls):
        """
        用来实现如何爬去first_url
        """
        raise NotImplementedError('爬虫必须实现first_url方法')

    def walk(self):
        """
        用来实现爬虫的动作
        """
        raise NotImplementedError('爬虫必须实现walk方法')

    def start(self):
        """
        启动爬虫
        """
        first_urls = self.__chromesome['FIRST_URL']
        requests = self.first_url(first_urls)

        if isinstance(requests,types.GeneratorType):
            for request in requests:
                callback = request.callback if request.callback else self.response
                self.fetch_sync(request,callback = callback)
                self.walk()
        else:
            pass

    def stop(self):
        pass

    def pause(self):
        #使用信号量使进程挂起，非阻塞
        pass

    def resume(self):
        #唤醒挂起进程
        pass

    def end(self):
        self.__pool.join()

    def response(self,response):
        """
        这里可以返回request或者数据对象
        """
        raise NotImplementedError('爬虫必须实现response方法')

    def url_extractor(self,rule):
        #返回URLExtractor
        pass

    def get_page_rule(self,number):
        """
        获取当前的PageRule对象
        """
        self.chromesome.get_page_rule(number)

    def push_master(self,request):
        """
        向master推送request
        """
        print 'push master'

    def push_data_pipeline(self,data):
        """
        向数据管道推送数据
        """
        print 'push data pipeline'

    def pull_scheduler(self):
        """
        从调度器拉request_json
        """
        print 'pull scheduler'

    @property
    def pool(self):
        return self.__pool

    @property
    def chromesome(self):
        return self.__chromesomes

    @property
    def pool(self):
        return self.__pool

    @property
    def scheduler(self):
        return self.__scheduler

    @property
    def name(self):
        return self.__name

    def _fetch(self,request,callback = None):
        """
        完成访问的请求,并把response转发到回调函数
        回调函数中进行页面和数据解析,可以将解析的内容通过yield或者return的方式返回
        yield方式会立刻将request放回调度器中
        return方式会等待全部完成后一起放回调度器中
        """
        response = request.fetch()
        request_or_datas = callback(response) if callback else self.response(response)

        if isinstance(request_or_datas,types.GeneratorType):
            #迭代生成器
            for r_or_d in request_or_datas:
                self._fetch_route(r_or_d)
        else:             
            self._fetch_route(request_or_datas)

    def _fetch_route(self,request_or_data):
        if isinstance(request_or_data,list):
            for r_or_d in request_or_data:
                self._fetch_request_or_data(r_or_data)
        else:
            self._fetch_request_or_data(request_or_data)
        
    def _fetch_reqeust_or_data(self,request_or_data):
        if isinstance(request_or_data,Request):
            self.push_master(r_or_d)
        elif isinstance(request_or_data,Data):
            self.push_data_pipeline(r_or_d)

    def _join(self):
        self.__pool.join()


class RuleLinkSpider(BaseSpider):
    
    #起始url
    def first_url(self,first_urls):
        for first_url in first_urls:
            yield Request(first_url,callback = self.first_response)

    def first_response(self,response):
        self.get_page_rule(0)

    def walk(self,url):
        self.scheduler.pull()

    #返回一个Reqeust对象，或者Request的对象列表,返回的Request自动发送到scheduler
    def response(self,response):
        print response



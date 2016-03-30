#*-*coding:utf8*-*
import types
import gevent.pool as GEV

import Araneae.db as DB
import Araneae.data as DT
import Araneae.dna.rule as PR
import Araneae.scheduler as SCH
import Araneae.extractor as EXT 
import Araneae.utils.http as UTL
import Araneae.net.request as REQ 
import Araneae.dna.chromesome as CHM 

"""
`spider.py` -- 爬虫组件
=======================
"""

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
        if isinstance(chromesome,CHM.BaseChromesome):
            self.__chromesome = chromesome
        else:
            raise TypeError('参数必须为Chromesome类型')

        self.__name = chromesome.get('SPIDER_NAME')
        self.__running_type = chromesome.running_type

        self.__pool = GEV.Pool(chromesome.getint('CONCURRENT_REQUESTS'))
        self.__scheduler = getattr(SCH,chromesome.scheduler)()

        if chromesome.running_type == CHM.RUNNING_TYPE_SINGLETON:
            self.__rpc = self.__scheduler
        elif chromesome.running_type == CHM.RUNNING_TYPE_DISTRIBUTED:
            #实例化rpc
            pass
                
        if chromesome.lasting:
            self.__data_pipeline = DB.generate_pipeline(**chromesome.lasting)

    def first_urls(self,first_urls):
        """
        用来实现如何爬去first_url
        """
        raise NotImplementedError('爬虫必须实现first_url方法')

    def parse(self,response):
        """
        这里可以返回request或者数据对象
        """
        raise NotImplementedError('爬虫必须实现parse方法')

    def start(self):
        """
        启动爬虫
        """
        first_urls = self.__chromesome['FIRST_URLS']
        
        if isinstance(first_urls,str):
            first_urls = [].append(first_urls)

        requests = self.first_urls(first_urls)

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

    def walk(self):
        """
        用来实现爬虫的动作
        """
        raise NotImplementedError('爬虫必须实现walk方法')


    def end(self):
        self.__pool.join()

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

    #从scheduler获取(pull)request，如果scheduler为空，进行延时重试，如果最后为空，结束爬虫
    def master_push(self,request):
        """
        向master推送request
        """
        print 'push master'

    def data_pipeline_push(self,data):
        """
        向数据管道推送数据
        """
        print 'push data pipeline'

    def scheduler_pull(self):
        """
        从调度器拉request_json
        """
        print 'pull scheduler'

    def get_page_rule(self,number):
        """
        获取当前的PageRule对象
        """
        return self.__chromesome.get_page_rule(number)

    @property
    def name(self):
        return self.__name

    @property
    def scheduler(self):
        return self.__scheduler

    def _fetch(self,request,callback = None):
        """
        完成访问的请求,并把response转发到回调函数
        回调函数中进行页面和数据解析,可以将解析的内容通过yield或者return的方式返回
        yield方式会立刻将request放回调度器中
        return方式会等待全部完成后一起放回调度器中
        """
        response = request.fetch()
        request_or_datas = getattr(self,callback)(response) if callback else self.parse(response)

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
        
    def _fetch_request_or_data(self,request_or_data):
        if isinstance(request_or_data,REQ.Request):
            self.push_master(r_or_d)
        elif isinstance(request_or_data,DT.Data):
            self.push_data_pipeline(r_or_d)

    def _join(self):
        self.__pool.join()


class RuleLinkSpider(BaseSpider):
    
    #起始url
    def first_urls(self,first_urls):
        for first_url in first_urls:
            if isinstance(first_url,str):
                yield REQ.Request(first_url,callback = 'first_parse')
            elif isinstance(fisrt_url,dict):
                yield REQ.json2request(first_url)

    def first_parse(self,response):
        first_page_rule = self.get_page_rule(0)
        self.page_rule_parse(first_page_rule,response)

    def parse(self,response):
        pass
        
    #开始进行调度、爬取和解析
    def walk(self):
        self.scheduler_pull()

    #返回一个Request对象，或者Request的对象列表,返回的Request自动发送到scheduler

    def page_rule_parse(self,page_rule,response):
        """
        PageRule规则解析
        """
        response_dom = EXT.response2dom(response)

        if page_rule.extract_url_type == PR.EXTRACT_URL_TYPE:
            urls = EXT.UrlExtractor(response_dom,**page_rule.extract_url_element)()
            
            for url in urls:
                url = UTL.replenish_url(response,url)
                
        elif page_rule.extract_url_type == PR.FORMAT_URL_TYPE:
            pass
        elif page_rule.extract_url_type == PR.NONE_URL_TYPE:
            #没有继续抽出的规则
            pass



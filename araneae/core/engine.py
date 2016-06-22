# coding:utf8 

"""控制spider的动作,例如start,stop,包括一些拉取操作，上推操作....."""

import os 
import time
import types
from enum import Enum
from psutil import Process

from Araneae.http.request import Request
from Araneae.core.agent import DownloaderAgent
from Araneae.man.exception import SchedulerEmpty
from Araneae.utils.request import urls_to_requests
from Araneae.utils.protocol import protocol_string_to_object


class EngineStatus(Enum):
    stop = 0
    running = 1
    pause = 2
    idle = 3

class Engine(object):

    def __init__(self, spider):
        self.status = EngineStatus.stop
        self.spider_name = spider.name
        self.spider_logger = spider.logger
        self.spider_callback = spider.callback
        self.settings = spider.settings

    def set_process(self):
        pid = os.getpid()
        self._pid = pid
        self._process = Process(pid)

    def set_running_type(self,distributed):
        """设置运行类型,singleton和distributed有不同的处理逻辑"""
        
        scheduler_cls = load_object(self.settings.get('SCHEDULER'))
        self._scheduler = scheulder_cls.from_spider(self)

        if distributed:
            self._master_rpc = None
        else:
            dupefiler = load_object(self.settings.get('DUPEFILTER'))
            self._dupefilter = dupefilter.from_spider(self)
            self._scheduler = SchedulerFactory(self._scheduler, self._dupefilter)            
            self._master_rpc = self._scheudler

    def set_downloader(self):
        """设置网络访问组件,根据不同的协议区分
        不同协议的区分在downloader中区分,就像一个真正的浏览器一样"""                                                                                                                   
        downloader_cls = load_object(self.settings,get('DOWNLOADER_AGENT'))
        self.downloader = downloader_cls.from_spider(spider)

    def set_pipeline(self):
        """设置数据管道,数据管道为多个时数据按顺序进入多个管道中"""

        pass

    def set_statscol(self):
        """设置统计收集器"""

        statscol_cls = load_object(self.settings,get('STATS_COLLECTION_LIST'))
        self._statscol = statscol_cls.from_spider(self)

    def set_middleware(self):
        """设置中间件管理器"""

        mw_manager_cls = load_object(self.settings,get('MIDDLEWARE_MANAGER'))
        self._mw_manager = mw_manager_cls.from_spider(self)

    def restart(self):
        pass
    
    def start(self):
        assert self.status==EngineStatus.stop, 'Spider engine already running'
        self.status = EngineStatus.start
        self.start_time = time.time()
        self.push_first_urls_to_scheduler()
        self.turbine()

    def stop(self):
        assert self.status!=EngineStatus.stop,'Spider engine already stop'
        self.status = EngineStatus.stop

    def pause(self):
        assert self.status!=EngineStatus.stop,'Spider engine already stop'
        self._process.suspend()
        self.status = EngineStatus.pause

    def resume(self):
        assert self.status==EngineStatus.pause,'Spider engine arent paused'
        self._process.resume()
        self.status = EngineStatus.running

    def turbine(self):
        """引擎为running状态,循环从调度器中取出待爬取得request,并将request,protocol,response送入callback中"""

        while self.status == EngineStatus.running:
            request,protocol = self.pull_request_from_scheduler()
            response = self.send_request(request)
            response and request.callback(protocol,response)

    def push_first_urls_to_scheduler(self):
        """将first_urls送入调度器中统一处理"""

        first_urls = self.settings['FIRST_URLS']
        fisrt_requests = urls_to_requests(frist_urls, callback = self.spider_callback)
        self.push_requests_to_scheduler(first_requests)
        
    def pull_request_from_scheduler(self):
        try:
            protocol_string = self._scheduler.pull()
        except SchedulerEmpty:
            self.spider_logger.info('Scheduler already emtpy,stop engine soon') 
            self.stop()  
            
        protocol = protocol_string_to_object(protocol_string)
        request = protocol.request
        return (request,protocol)

    def push_request_to_scheduler(self, req):
        if isinstance(reqs, Request):
            self._scheduler.push(req)
    
    def push_requests_to_scheduler(self, reqs):
        if isinstance(reqs, (list,GeneratorType)):
            for req in reqs:
                self.push_request_to_scheudler(req)    

    def push_data_to_pipeline(self):
        pass

    def request_backout(self,priority=None):
        pass

    def send_request(self, req):
        """发送请求"""
        
        return  self._downloader.send(req)




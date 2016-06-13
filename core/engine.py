# coding:utf8 

"""控制spider的动作,例如start,stop,包括一些拉取操作，上推操作....."""

import os 
import time
from psutil import Process

from Araneae.man.excepitons import SchedulerEmpty
from Araneae.utils.protocol import protocl_string_to_object


class Engine(object):

    def __init__(self, spider):
        self.runing = Flase
        self.spider_name = spider.name
        self.spider_logger = spider.logger
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
        http_downloader_cls = load_object(self.settings,get('HTTP_DOWNLOADER'))
        #file_downloader_cls = load_object(self.settings,get('FILE_DOWNLOADER'))
        #ftp_downloader_cls = load_object(self.settings,get('ftp_DOWNLOADER'))
        self._http_downloader = http_downloader_cls.from_spider(self)
        #self._file_downloader = file_downloader_cls.from_spider(self)
        #self._ftp_downloader = ftp_downloader_cls.from_spider(self)
    
    def set_pipeline(self):
        """设置数据管道,数据管道为多个时数据按顺序呢进入多个管道中"""

        pass

    def set_statscol(self):
        """设置统计收集器"""

        statscol_cls = load_object(self.settings,get('STATS_COLLECTION'))
        self._statscol = statscol_cls.from_spider(self)

    def set_middleware(self):
        """设置中间件"""

        mw_manager_cls = load_object(self.settings,get('MIDDLEWARE_MANAGER'))
        self._mw_manager = mw_manager_cls.from_spider(self)

    
    def start(self):
        assert not self.running, 'Spider engine already running'
        self.runing = True
        self.start_time = time.time()

    def stop(self):
        assert self.running,'Spider engine already stop'
        self.running = False

    def pause(self):
        self._process.suspend()

    def resume(self):
        self._process.resume()

    def pull_request_from_scheduler(self):
        try:
            protocol_string = self._scheduler.pull()
        except SchedulerEmpty:
            self.spider_logger.info('Scheduler already emtpy,stop engine soon') 
            self.stop()  
            
        protocol = protocol_string_to_object(protocol_string)
        request = protocol.request
        return (request,protocol)


    def push_request_to_master(self):
        pass

    def push_data_to_pipeline(self):
        pass

    def request_backout(self):
        pass

    def next_response(self):
        """下一个请求响应体,response中包含很多解析需要的信息"""
        
        request,protocol = self.pull_request_from_sheduler()
        return  self._downloader.send(request)

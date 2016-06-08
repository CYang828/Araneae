#!coding:utf8

import os

from Araneae.utils.log import get_logger
from Araneae.utils.settings import Settings
from Araneee.utils.loader import load_object
from Araneae.singleton import SchedulerFactory
from Araneae.utils.livetracker import LiveObject
from Araneae.downloaders.http import HttpDownloader


class Spider(LiveObject):
    """
    爬虫基类
    """

    def __init__(self, setting_path, distributed=False):
        self._pid = os.getpid()
        self.settings = Settings(setting_path)
        self._initialize(distributed)

    def _initialize(self,distributed):
        """
        初始化spider组件
        """
        self.set_spider_name()
        self.set_running_type(distributed)
        self.set_downloader()
        self.set_logger()
        self.set_pipeline()
        self.set_middleware()
        self.set_statscol()

    def reset(self,distributed):
        """
        重新加载配置文件,构建spider
        """
        self.reset_settings()
        self._initialize(distributed)

    def reset_settings(self):
        """
        重新加载配置文件
        """
        self.settings.reset()

    def set_spider_name(self):
        """
        设置爬虫名
        """
        self.name = self.setttings.get('SPIDER_NAME', dont_empty=True)

    def set_running_type(self,distributed):
        """
        设置运行类型
        singleton和distributed有不同的处理逻辑
        """
        self._scheduler = load_object(self.settings.get('SCHEDULER')).from_spider(self)

        if distributed:
            pass
        else:
            self._dupefilter = load_object(self.settings.get('DUPEFILTER')).from_spider(self)
            self._scheduler = SchedulerFactory(self._scheduler, self._dupefilter)            
            self._rpc = self._scheudler

    def set_downloader(self):
        """
        设置网络访问组件,根据不同的协议区分
        """
        self._http_downloader = HttpDownloader().from_spider(self)
        #self._file_downloader = 
        #self._ftp_downloader = 

    def set_logger(self):
        """
        设置日志格式及路径
        """
        log_path = self.settings.get['LOG_PATH']
        log_level = self.settings.get['LOG_LEVEL']
        terminal_log_level = self.settings.get['TERMINAL_LOG_LEVEL']
        self._logger = get_logger(LOG_PATH)
        self._logger.setLevel(log_level)
        self._terminal_logger = ger_logger(__name__)
        self._terminal_logger.setLevel(terminal_log_level)

    def set_pipeline(self):
        """
        设置数据管道,数据管道为多个时数据按顺序呢进入多个管道中
        """
        pass

    def set_middleware(self):
        """
        设置中间件
        """
        pass

    def set_statscol(self):
        """
        设置统计收集器
        """
        pass

    def get_pid(self):
        """
        获取当前进程id
        """
        return self._pid




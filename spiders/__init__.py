#!coding:utf8

import os

from Araneae.utils.log import get_logger
from Araneae.utils.settings import Settings
from Araneee.utils.loader import load_object
from Araneae.singleton import SchedulerFactory
from Araneae.utils.livetracker import LiveObject
from Araneae.downloaders.http import HttpDownloader
from Araneae.core.middleware import MiddlewareManager


"""spider中是一些爬虫独有的属性,不需要包含动作"""

logger = get_logger(__name__)

class Spider(LiveObject):
    """
    爬虫基类
    """

    def __init__(self, setting_path, distributed=False):
        self._pid = os.getpid()
        self.settings = Settings(setting_path)
        self._initialize(distributed)

    def _initialize(self,distributed):
        """初始化spider组件"""

        self.set_spider_name()
        self.set_running_type(distributed)
        self.set_downloader()
        self.set_logger()
        self.set_pipeline()
        self.set_middleware()
        self.set_statscol()

    def reset(self,distributed):
        """重新加载配置文件,构建spider"""

        self.reset_settings()
        self._initialize(distributed)

    def reset_settings(self):
        """重新加载配置文件"""

        self.settings.reset()

    def set_spider_name(self):
        """设置爬虫名"""

        self.name = self.setttings.get('SPIDER_NAME', dont_empty=True)

    def set_running_type(self,distributed):
        """设置运行类型
        singleton和distributed有不同的处理逻辑"""

        scheduler_cls = load_object(self.settings.get('SCHEDULER'))
        self._scheduler = scheulder_cls.from_spider(self)

        if distributed:
            pass
        else:
            dupefiler = load_object(self.settings.get('DUPEFILTER'))
            self._dupefilter = dupefilter.from_spider(self)
            self._scheduler = SchedulerFactory(self._scheduler, self._dupefilter)            
            self._rpc = self._scheudler

    def set_downloader(self):
        """设置网络访问组件,根据不同的协议区分"""

        http_downloader_cls = load_object(self.settings,get('HTTP_DOWNLOADER'))
        #file_downloader_cls = load_object(self.settings,get('FILE_DOWNLOADER'))
        #ftp_downloader_cls = load_object(self.settings,get('ftp_DOWNLOADER'))
        self._http_downloader = http_downloader_cls.from_spider(self)
        #self._file_downloader = file_downloader_cls.from_spider(self)
        #self._ftp_downloader = ftp_downloader_cls.from_spider(self)

    def set_logger(self):
        """设置日志格式及路径"""

        log_path = self.settings.get('LOG_PATH')
        log_level = self.settings.get('LOG_LEVEL')
        terminal_log_level = self.settings.get('TERMINAL_LOG_LEVEL')
        self.logger = get_logger(log_path)
        self.logger.setLevel(log_level)

    def set_pipeline(self):
        """设置数据管道,数据管道为多个时数据按顺序呢进入多个管道中"""

        pass

    def set_middleware(self):
        """设置中间件"""

        mw_manager_cls = load_object(self.settings,get('MIDDLEWARE_MANAGER'))
        self._mw_manager = mw_manager_cls.from_spider(self)

    def set_statscol(self):
        """设置统计收集器"""

        statscol_cls = load_object(self.settings,get('STATS_COLLECTION'))
        self._statscol = statscol_cls.from_spider(self)

    def get_pid(self):
        """获取当前进程id"""

        return self._pid

    def pull_next_request(self):
        """从调度器中获取下一个request"""
    
        pass

    def push_request(self):
        """将request送入调度器"""

    def 

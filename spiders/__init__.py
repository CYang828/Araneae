#!coding:utf8

import os

from Araneae.core.engine import Engine
from Araneae.utils.log import get_logger
from Araneae.rules.picker import RulePicker
from Araneae.utils.settings import Settings
from Araneae.utils.loader import load_object
from Araneae.singleton import SchedulerFactory
from Araneae.utils.livetracker import LiveObject
from Araneae.downloaders.http import HttpDownloader
from Araneae.core.middleware import MiddlewareManager


"""spider中是一些爬虫独有的属性,不需要包含动作"""

logger = get_logger(__name__)

class Spider(LiveObject):
    """爬虫基类
    继承时必须设置rule_path类成员变量,用来指定唯一的规则类协助spider进行解析"""

    def __init__(self, setting_path, distributed=False):
        self._pid = os.getpid()
        settings = Settings(setting_path)
        self.settings = settings
        self.callback = self.parse
        self.engine = Engine(spider)
        self._initialize()

    def _initialize(self):
        """初始化spider组件"""

        self.set_name()
        self.set_logger()

    def reset(self,distributed):
        """重新加载配置文件,构建spider"""

        self.reset_settings()
        self._initialize(distributed)

    def reset_settings(self):
        """重新加载配置文件"""

        self.settings.reset()

    def set_callback(self,callback):
        """设置回调函数名,如果不设置默认为self.parse"""

        self.callback = callback

    def set_name(self):
        """设置爬虫名"""

        self.name = self.setttings.get('SPIDER_NAME', dont_empty=True)
    
    def set_logger(self):
        """设置日志格式及路径"""

        log_path = self.settings.get('LOG_PATH')
        log_level = self.settings.get('LOG_LEVEL')
        terminal_log_level = self.settings.get('TERMINAL_LOG_LEVEL')
        self.logger = get_logger(log_path)
        self.logger.setLevel(log_level)

    def set_rule_picker(self):
        """设置rule picker,用来管理页面爬取rules"""
        assert self.rule_class_path, 'Spider must define class member variable rule_path'
        self.rule_picker = RulePicker(self.settings, self.rule_class_path)

    def start(self):
        self.engine.start()

    def stop(self):
        self.engine.stop()

    def pause(self):
        self.engine.pause()

    def resume(self):
        self.engine.resume()

    def parse_response(self):
        pass

    def parse(self,protocol,response):
        pass

# coding:utf8

from collections import defaultdict

from Araneae.loader import load_object
from Araneae.utils.log import get_logger


logger = get_logger(__name__)

class MiddlewareManager(object):

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.middleware_methods = default_dict(list)

        for mv in middlewares:
            self._add_middleware_method(mv)

    @classmethod
    def from_spider(self, spider):
        settings = spider.settings
        mwlist = setttings.getlist('MIDDLEWARE_LIST')
        middlewares = []

        for clspath in mwlist;
            mwcls = load_object(clspath)               
            
            if hasattr(mwcls, 'from_spider'):
                mw = mwcls.from_spider(spider)
            elif hasattr(mwcls, 'from_setting'):
                mw = mwcls.from_setting(settings)
            else:
                mw = mwcls()

            middlewares.append(mw)

        return cls(*middlewares)

    def _add_middleware_method(self,middleware):
        if hasattr(mv, 'open_spider'):
            self.middleware_methods['open_spider'].append(mv.open_spider)

        if hasattr(mv, 'process_before_request'):
            self.middleware_methods['process_before_request'].append(mv.process_before_request)

        if hasattr(mv, 'process_after_response'):
            self.middleware_methods['process_after_response'],append(mv.process_after_response)

        if hasattr(mv, 'process_before_pipeline'):
            self.middleware_method['process_before_pipeline'].append(mv.process_before_pipeline)

        if hasattr(mv, 'process_before_download'):
            self.middleware_method['process_before_download'].append(mv.process_before_download)

        if hasattr(mv, 'close_spider'):
            self.middleware_method['close_spider'].insert(0, mv.close_spider)
        
    def _process_chain(self, methods):
        for m in metods:
            yield m

    def open_spider(self):
        return self._process_chain(self.middleware_method['open_spider'])
 
    def close_spider(self):
        return self._process_chain(self.middleware_method['close_spider'])

    #所有类型的方法

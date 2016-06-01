#!coding:utf8

import six

from Araneae.compat import json as Json
from Araneae.http.request import Request
from Araneae.utils.request import request_pickle


class SchedulerProtocol(object):

    def __init__(self,request, scheduler_name = None, rule_number = None, associate = None, aid = None, url_routes = None, priority = 0):
        assert isinstance(request, Request), 'Scheduler protocol第一个参数必须是Request: [%s]' % type(request).__name__
        self._request = request
        assert isinstance(scheduler_name, six.string_types), '调度器名称必须是字符串类型: [%s]' % type(scheduler_name).__name__
        self.scheduler_name = scheduler_name
        assert isinstance(rule_number, int), '规则号码必须是int类型: [%r]' % rule_number
        self.rule_number = rule_number

        self.associate = associate or False
        self.aid = aid or None
        self._url_routes = url_routes or []

        self._priority = priority

    def __str__(self):
       return '<SchedulerProtocol %r %s %d>' % (self._request, self.scheduler_name, self.rule_number)

    def to_json(self):
        return {'request':request_pickle(self._request),'scheduler_name':self.scheduler_name,'rule_number':self.rule_number,
                'associate':self.associate,'aid':self.aid,'url_routes':self._url_routes}

    def to_json_string(self):
        return Json.dumps(self.to_json(), ensure_ascii = True)

    def replace(self, *args, **kwargs):
        for x in ['request','scheduler_name','rule_number','associate','aid','url_routes']:
            kwargs.setdefault(x, getattr(self,x))
        
        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

    def copy(self):
        return self.replace()

    def add_url_route(self,url_route):
        self._url_routes.append(url_route)

    @property
    def request(self):
        return self._request

    @property
    def priority(self):
        return self._priority

    @property
    def url_routes(self):
        """返回列表拷贝"""
        return self._url_routes[:]
       
    @property
    def url_routes_string(self):
        return '->'.join(self._url_routes)
    
        
if __name__== '__main__':
    from Araneae.http.request import Request
    r = Request('www.baidu.com')
    protocol = SchedulerProtocol(r,scheduler_name = 'demo',rule_number = 1) 
    print protocol
    b = protocol.copy()
    print b
    print id(protocol)
    print id(b)



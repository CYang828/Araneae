#!coding:utf8

import gevent 
import gevent.pool
import gevent.monkey
gevent.monkey.patch_all()
import requests

from Araneae.downloaders import Agent
from Araneae.http.response import Response


DEFAULT_RETRIES = 0
DEFAULT_POOLSIZE = 10
DEFAULT_POOLBLOCK = False
DEFAULT_POOL_TIMEOUT = None
DEFAULT_CONCURENT_REQUESTS = 10

class HttpAgent(Agent):

    def __init__(self,pool_connections=DEFAULT_POOLSIZE, pool_maxsize=DEFAULT_POOLSIZE, max_retries=DEFAULT_RETRIES, 
                 pool_block=DEFAULT_POOLBLOCK,concurent_requests = DEFAULT_CONCURENT_REQUESTS):
        self._set_session(pool_connections,pool_maxsize,max_retries)
        self._set_asyn_pool(concurent_requests)

    def _set_session(self,pool_connections,pool_maxsize,max_retries):
        self._session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(pool_connections=pool_connections, pool_maxsize=pool_maxsize,max_retries=max_retries)
        self._session.mount('http://',adapter)
        self._session.mount('https://',adapter)
        self._session.mount('ftp://',adapter)

    def _set_asyn_pool(self,concurent_requests):
        self._request_pool = gevent.pool.Pool(concurent_requests)

    def send(self, protocol, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        proxies = protocol.request.proxies
        self._request_pool.spawn(self._send, protocol, stream, timeout, verify, cert, proxies)

    def _send(self, protocol, stream, timeout, verify, cert, proxies):
        request = protocol.request
        prepare_request = self._session.prepare_request(request)
        response = self._session.send(prepare_request, stream=stream, timeout=timeout, verify=verify, cert=cert, proxies = proxies)

        response.ok and request.callback and (request.callback(protocol,response) or self._empty_callback(protocol,response))
        not response.ok and request.errback and (resuest.errback(protocol,response) or self._default_errback(protocol,response))

        return Response(response)

    def download(self, protocol, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        #文件request放到调度器中，调用download进行下载处理
        pass

    def _download(self):
        pass

    def _empty_callback(self,protocol,response):
        print '抽取内容为空'

    def _default_errback(self,protocol,response):
        print 'defualt errback'


if __name__ == '__main__':
    from Araneae.http.request import Request
    from Araneae.protocols.scheduler import SchedulerProtocol

    class Test(object):

        def test(self,protocol,response):
            print 'hello python'
            return 'a'

    a = Test()

    request1 = Request('www.baidu.com',callback = a.test)
    protocol1 = SchedulerProtocol(request1,scheduler_name = 'demo',rule_number = 1)
    request2 = Request('www.baidu.com')
    protocol2 = SchedulerProtocol(request2,scheduler_name = 'demo',rule_number = 1)
    agent = HttpAgent()
    agent.send(protocol1)
    agent.send(protocol2)

    gevent.wait()

#!coding:utf8

from Araneae.utils.livetracker import LiveObject
from Araneae.http.request import (Request,DEFAULT_REQUEST_METHOD)


class FileRequest(Request, LiveObject):

    def __init__(self, download_path, *args, **kwargs):
        self.download_path = download_path

    def __str__(self):
        return '<FileRequest %s %s %s>' % (self.method, self.url, self.download_path)

    __repr__ = __str__

    def to_json(self):
        return {'url':self.url,'download_path':self.download_path,'method':self.method,'encoding':self._encoding,'callback':self.callback,
                'proxies':self.proxies,'headers':self.headers,'data':self.data,'params':self.params,
                'auth':self.auth,'cookies':self.cookies,'json':self.json,
                'dont_filter':self.dont_filter,'errback':self.errback}

    def replace(self, *args, **kwargs):
        for x in ['url','download_path','callback','method','encoding','proxies','priority','headers',
                  'data','params','auth','cookies','json','dont_filter','errback']:
            kwargs.setdefault(x, getattr(self,x))                                                                                                                   

        cls = kwargs.pop('cls', self.__class__)
        return cls(*args, **kwargs)

     

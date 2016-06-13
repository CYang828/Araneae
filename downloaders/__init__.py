#!coding:utf8

from Araneae.utils.livetracker import LiveObject

class DownloaderAgent(LiveObject):
    """downloader代理，用来管理各种下载器,每种下载器中必须指定它能够处理的协议和类型"""
        
    def __init__(self, *downloaders):
        self._downloaders = downloaders
        
    @classmethod
    def from_spider(self, spider):
        settings = spider.settings
        downloader_list = settings['DOWNLOADER_LIST']
        downloaders = []

        for clspath in downloader_list:
            dwcls = load_object(dwcls)
            
            if hasattr(dwcls, 'from_spider'):
                dw = dwcls.from_spider(spider)
            elif hasattr(mwcls, 'from_setting'):
                dw = dwcls.from_setting(settings)
            else:
                dw = dwcls()

            downloaders.append(dw)

        return cls(*downloaders)           

    def _choose_downloader(self,request):
        for dw in self.downloaders:
            if request.scheme in dw.schemes:
                return dw

    def send(self,request):
        downloader = self._choose_downloader(request)   
        downloader.send(request)

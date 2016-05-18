#*-*coding:utf8*-*
import os
import re
import time
import requests
import gevent as GEV
import gevent.lock as GEVL
import gevent.pool as GEVP
import gevent.queue as GEVQ
import gevent.thread as GEVT

import Araneae.file as FILE
import Araneae.utils.http as UTLH

DEFAULT_DOWNLOAD_TIMEOUT = 30

class DownloadProcessor(object):

    def __init__(self,file_path,response,file_obj):
        content_type_dict = {'application/octet-stream' : self.octet_stream,
                             'image/jpeg'               : self.image_jpeg}

        content_type = response.headers['Content-Type']
        method = content_type_dict.get(content_type)

        if method:
            method(file_path,response,file_obj)
        else:
            raise TypeError('没有%s类型的content处理器' % content_type)

    def octet_stream(self,file_path,response,file_obj):
        header_context = response.headers['Content-Disposition']
        match = re.search(r'[.]*?filename=(.*)', header_context)

        if match:
            file_name = match.group(1)
            file_type = file_name[file_name.rfind('.'):]
            file_path = file_path +file_obj.file_name + file_type

            with open(file_path, "wb") as f:
                f.write(response.content)       
        else:
            raise TypeError('下载错误')
               
    def image_jpeg(self,content):
        pass

class BaseDownloader(object):

    def __init__(self,file_path):
        self._file_path = file_path
 
        try:
            os.makedirs(file_path)       
        except OSError:
            pass

        self._queue = GEVQ.Queue()
        self._pool = GEVP.Pool()
        #download_threads = [GEV.spawn(self._processor)]
        download_threads = GEVT.start_new_thread(self._processor)

    def _processor(self):
        while True:
            #队列为空时阻塞
            file_obj = self._queue.get() 
            self._pool.spawn(self._download,file_obj)
            time.sleep(10)
            

    def _download(self,file_obj):
        method = UTLH.validate_method(file_obj.method)

        print '下载文件,请求体%s' % file_obj.json()
        #try:
        response = getattr(requests,method)(file_obj.url,
                                            proxies = file_obj.proxies,
                                            headers = file_obj.headers,
                                            cookies = file_obj.cookies,
                                            timeout = DEFAULT_DOWNLOAD_TIMEOUT)

        DownloadProcessor(self._file_path,response,file_obj)
        #except:
        #    raise TypeError('请求地址错误')

    def push(self,file_obj):
        raise NotImplementedError('下载器必须实现push方法')

    def full(self):
        raise NotImplementedError('下载器必须实现full方法')

class LocalDownloader(BaseDownloader):
    
    def push(self,file_obj):
        if isinstance(file_obj,FILE.File):
            try:
                #队列满抛出异常,由生产者决定操作
                self._queue.put_nowait(file_obj)
            except Full:
                raise TypeError('队列满')
        else:
            raise TypeError('下载类型必须为File')

    def full(self):
        return self._queue.full()


if __name__ == '__main__':
    from gevent import monkey; monkey.patch_all()
    import time
    from Araneae.file import File
    
    file_info = {'file_name':'1.zip','headers':{'Cookie':'DWRSESSIONID=6HgxZXzGbFaZ6JosPj9wOdDN*hl; JSESSIONID=abcymybCrWJaQcZz7F6rv; jsessionid=2F66B2CCE767E51051EFEF49CD81EFB8'}} 
    file_obj = File('http://czy.jtyhjy.com/jty/tbkt/downLoadAttach.action?articleId=3825793&urlId=1',**file_info)

    local = LocalDownloader('/home/zhangchunyang/download/')
    local.push(file_obj)

#*-*coding:utf8*-*

import gevent.lock as GEVL
import gevent.pool as GEVP
import gevent.queue as GEVQ
import gevent.thread as GEVT

import Araneae.file as FILE
import Araneae.utils.http as UTLH

DEFAULT_DOWNLOAD_TIMEOUT = 30

class DownloadProcessor(object):

    def __init__(self,response,file_obj):
        content_type_dict = {'application/octet-stream' : self.octet_stream,
                             'image/jpeg'               : self.image_jpeg}

        method = content_type_dict.get(response.headers['Content-Type'])

        if method:
            method(content,file_obj)
        else:
            raise TypeError('没有%s类型的content处理器' % content_type)

    def octet_stream(self,response,file_obj):
        header_context = response.headers['Content-Disposition']
        match = re.search(r'[.]*?filename=(.*)', header_context)

        if match:
            file_name = match.group(1)

            print 'Download FileName[%s][%s]' % (fileName, downloadItem.file_path)

            file_name = file_obj.file_path

            with open(file_name, "wb") as f:
                f.write(response.content)       

        else:
            raise TypeError('下载错误')
               
    def image_jpeg(self,content):
        pass

class BaseDownloader(object):

    def __init__(self):
        self._queue = GEVQ.Queue()
        self._pool = GEVP.Pool()

    def _processor(self):
        while True:
            #队列为空时阻塞
            file_obj = self._queue.get() 
            self.pool.spawn(self._download,file_obj)

    def _download(self,file_obj):
        method = UTLH.validate_method(file_obj.method)

        try:
            response = getattr(requests,method)(file_obj.url,
                                                proxies = file_obj.proxies,
                                                headers = file_obj.headers,
                                                cookies = file_obj.cookie,
                                                timeout = DEFAULT_DOWNLOAD_TIMEOUT)

            DownloadProcessor(response,file_obj)
        except:
            raise TypeError('请求地址错误')

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

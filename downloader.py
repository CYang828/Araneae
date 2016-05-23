#*-*coding:utf8*-*
import os
import re
import time
import requests
import gevent.pool as GEVP
import gevent.thread as GEVT

import Araneae.file as FILE
import Araneae.scheduler as SCH
import Araneae.utils.http as UTLH
import Araneae.man.exception as EXP

DEFAULT_DOWNLOADER_TIMEOUT = 30
DEFAULT_DOWNLOADER_SLEEP_TIME = 5
DEFAULT_DOWNLOADER_POOL_SIZE = 10
DEFAULT_DOWNLOADER_SCHEDULER_TIMEOUT = 5

DOWNLOADER_FINISH_FLAG = 'downloader_finish'


class DownloadProcessor(object):
    """
    下载处理器

    根据下载内容的Content-Type不同,处理逻辑不同
    """

    def __init__(self, file_path, response, file_obj):
        content_type_dict = {'application/octet-stream': self.octet_stream,
                             'image/jpeg': self.image_jpeg}

        content_type = response.headers['Content-Type']
        method = content_type_dict.get(content_type)

        if method:
            method(file_path, response, file_obj)
        else:
            raise EXP.DownloaderError('没有%s类型的content处理器' % content_type)

    def octet_stream(self, file_path, response, file_obj):
        header_context = response.headers['Content-Disposition']
        match = re.search(r'[.]*?filename=(.*)', header_context)

        if match:
            file_name = match.group(1)
            file_type = file_name[file_name.rfind('.'):]
            file_path = file_path + file_obj.file_name + file_type

            with open(file_path, "wb") as f:
                f.write(response.content)
        else:
            raise EXP.DownloaderError('HTTP协议中没有文件名')

    def image_jpeg(self, content):
        pass


class BaseDownloader(object):
    """
    下载器基础类

    可以根据需求替换下载器中的调度器和去重器
    """

    def __init__(self,
                 file_path,
                 scheduler,
                 dupefilter,
                 download_sleep_time=DEFAULT_DOWNLOADER_SLEEP_TIME,
                 pool_size=DEFAULT_DOWNLOADER_POOL_SIZE):
        self._file_path = file_path
        self._download_sleep_time = download_sleep_time

        try:
            os.makedirs(file_path)
        except OSError as e:
            pass

        self._scheduler = SCH.DupeScheduler(scheduler, dupefilter)
        self._pool = GEVP.Pool(pool_size)
        download_threads = GEVT.start_new_thread(self._processor)
        self._run = True

    def _processor(self):
        while self._run:
            #队列为空时阻塞
            file_json = self._scheduler.pull(
                DEFAULT_DOWNLOADER_SCHEDULER_TIMEOUT)

            if file_json == DOWNLOADER_FINISH_FLAG: 
                print '下载器结束'
                break
            elif not file_json:
                continue

            file_obj = FILE.File.instance(file_json)

            self._pool.spawn(self._download, file_obj)
            time.sleep(self._download_sleep_time)

    def _download(self, file_obj):
        method = UTLH.validate_method(file_obj.method)

        response = getattr(requests, method)(
            file_obj.url,
            proxies=file_obj.proxies,
            headers=file_obj.headers,
            cookies=file_obj.cookies,
            timeout=DEFAULT_DOWNLOADER_TIMEOUT)

        DownloadProcessor(self._file_path, response, file_obj)

    def push(self, file_obj):
        raise NotImplementedError('下载器必须实现push方法')

    def full(self):
        raise NotImplementedError('下载器必须实现full方法')

    @property
    def gag(self):
        return self._gag

    @gag.setter
    def gag(self, gag):
        self._gag = gag


class WorkerDownloader(BaseDownloader):
    """
    由worker管理的下载器

    """

    def push(self, file_json):
        self._scheduler.push(file_json)


class DistributedDownloader(BaseDownloader):
    """
    单独管理的下载器
    """

    def push(self, file_json):
        self._scheduler.push(file_json)


if __name__ == '__main__':
    import time
    import gevent
    from gevent import monkey

    import Araneae.utils.contrib as UTLC

    monkey.patch_all()

    file_info = {
        'file_name': '1.zip',
        'headers':
        {'Cookie':
         'DWRSESSIONID=6HgxZXzGbFaZ6JosPj9wOdDN*hl; JSESSIONID=abcymybCrWJaQcZz7F6rv; jsessionid=2F66B2CCE767E51051EFEF49CD81EFB8'
         }
    }

    file_obj = FILE.File(
        'http://czy.jtyhjy.com/jty/tbkt/downLoadAttach.action?articleId=3825793&urlId=1',
        **file_info)

    redis_conf = {'host': '172.18.4.52',
                  'port': 6379,
                  'db': 0,
                  'password': None,
                  'timeout': 5,
                  'charset': 'utf8'}

    memory_scheduler = UTLC.load_class('Araneae.scheduler.MemoryScheduler',
                                       'demo')
    memory_dupefilter = UTLC.load_class('Araneae.dupefilter.MemoryDupeFilter',
                                        'demo')

    #redis_scheduler = UTLC.load_class('Araneae.scheduler.RedisScheduler',
    #                                  'demo', **redis_conf)
    #redis_dupefilter = UTLC.load_class('Araneae.dupefilter.RedisDupeFilter',
    #                                   'demo', **redis_conf)

    memory_worker = WorkerDownloader('/home/zhangchunyang/download/',
                                     memory_scheduler, memory_dupefilter)
    memory_worker.push(file_obj.json)

    #redis_worker = WorkerDownloader('/home/zhangchunyang/download/',
    #                                redis_scheduler, redis_dupefilter)
    #redis_worker.push(file_obj.json)
    memory_worker.push(DOWNLOADER_FINISH_FLAG)

    gevent.wait()

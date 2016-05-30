#*-*coding:utf8*-*

import re
import sys
import time
import copy
import types
import urlparse
import hashlib
import bson as BS
import gevent as GEV
import gevent.pool as GEVP

import Araneae.data as DT
import Araneae.file as FILE
import Araneae.dna.rule as PR
import Araneae.pipeline as PPL
import Araneae.downloader as DL
import Araneae.scheduler as SCH
import Araneae.extractor as EXT
import Araneae.utils.log as UTLL
import Araneae.middleware as MID
import Araneae.net.request as REQ
import Araneae.man.exception as EXP
import Araneae.utils.contrib as UTLC
import Araneae.dna.chromesome as CHM
"""
`spider.py` -- 爬虫基类和个性化爬虫实现
=======================================
"""


class BaseSpider(object):
    """
    每个spider必备:
        +爬虫名,用来唯一标识一个爬虫
        +爬虫运行类型:#Singleton单机模式(不指定时默认为该模式),Distributed(分布式,需要启动master,所有功能都能使用)
        +chromesome,配置爬取规则
        +pool,用来爬取任务,pool的大小可以限制爬虫的速度
        +thread_id,每个爬虫都在一个thread中,用来管理该线程

        +scheduler,用来调度任务
        +data_pipeline,传输数据管道,根据配置生成(可选)
        +rpc对象,如果为单机模式,rpc关联到scheduler进行push,单机模式下功能退化,只能满足简单的爬虫功能(rpc对象必须有一个和scheduler相同的push接口)
        ?????rpc对象是共用一个还是每个spider用一个?????????????????
        +downloader下载器,用来下载文件,可以是单机也可以是远程,远程会是一个rpc对象
        ?????downloader对象是共用一个还是每个spider用一个?????????????????

    """

    def __init__(self, chromesome):
        """
        初始化spider必要参数，
        错误预检查，防止出现运行一段时间出现错误

        参数:
            chromesome:爬虫配置(必须为BaseChromesome子类)

        """
        if isinstance(chromesome, CHM.BaseChromesome):
            self.__chromesome = chromesome
        else:
            raise EXP.ChromesomeException('spider的参数必须为Chromesome类型')

        self.__name = chromesome.spider_name
        self.__running_type = chromesome.running_type

        #运行方式为分布式时,rpc对象与master通信
        #master需要根据spider name不同分别放入不同的shceduler和dupefileter中
        #调度器和rpc使用的都是request对象的json序列化
        #运行方式为单机时,rpc对象为调度器对象
        if chromesome.running_type == CHM.RUNNING_TYPE_SINGLETON:
            scheduler = UTLC.load_class(chromesome.scheduler, chromesome.spider_name, **chromesome.scheduler_conf)
            dupefilter = UTLC.load_class(chromesome.dupefilter, chromesome.spider_name, **chromesome.dupefilter_conf)

            self.__scheduler = SCH.DupeScheduler(scheduler, dupefilter)
            self.__rpc = self.__scheduler
        elif chromesome.running_type == CHM.RUNNING_TYPE_DISTRIBUTED:
            pass

        self.__pool = GEVP.Pool(chromesome.concurrent_requests)

        #用于屏幕显示的logger
        self.__console_logger = UTLL.BaseLogger(chromesome.spider_name)

        #用于文件输出的logger
        log_path = chromesome.log_path if chromesome.log_path else (sys.path[0] + '/' + chromesome.spider_name + '.log')
        self.__file_logger = UTLL.BaseLogger(log_path)

        #一个spider产生的数据放入一个与spider同名的库中
        if chromesome.lasting:
            self.__data_pipeline = PPL.generate_pipeline(**chromesome.lasting)
            self.__data_pipeline.select_db(self.__name)

        #初始化下载器
        downloader_scheduler = UTLC.load_class(chromesome.scheduler, 'Downloader:' + chromesome.spider_name, **chromesome.scheduler_conf)
        downloader_dupefilter = UTLC.load_class(chromesome.dupefilter, 'Downloader:' + chromesome.spider_name, **chromesome.dupefilter_conf)
        self.__downloader = DL.WorkerDownloader('%s/%s/' % (chromesome.downloader_path, self.__name), downloader_scheduler, downloader_dupefilter)

        self._scheduler_retry_time = chromesome.scheduler_retry_time
        self._scheduler_retry_interval = chromesome.scheduler_retry_interval

        self._request_timeout = chromesome.request_timeout
        self._request_sleep_time = chromesome.request_sleep_time
        self._login_header = chromesome.login_header
        self._middle_data_collection = chromesome.middle_data_collection
        self._merge_data_collection = chromesome.merge_data_collection

        #生成中间件对象,预检查
        self._request_middleware = []
        self._data_middleware = []
        self._file_middleware = []

        for request_middleware in chromesome.request_middleware:
            print request_middleware
            request_middleware = UTLC.load_class(request_middleware)

            if not isinstance(request_middleware, MID.RequestMiddleware):
                raise EXP.MiddlewareException('request中间件必须继承RequestMiddleware')

            self._request_middleware.append(request_middleware)

        for data_middleware in chromesome.data_middleware:
            data_middleware = UTLC.load_class(data_middleware)

            if not isinstance(data_middleware, MID.DataMiddleware):
                raise EXP.MiddlewareException('data中间件必须继承DataMiddleware')

            self._data_middleware.append(data_middleware)

        for file_middleware in chromesome.file_middleware:
            file_middleware = UTLC.load_class(file_middleware)

            if not isinstance(file_middleware, MID.FileMiddleware):
                raise EXP.MiddlewareException('file中间件必须继承FileMiddleware')

            self._file_middleware.append(file_middleware)

    def _fetch(self, request, **args):
        """
        完成访问的请求,并把response转发到回调函数
        回调函数中进行页面和数据解析,可以将解析的内容通过yield或者return的方式返回
        yield方式会立刻将request放回调度器中
        return方式会等待全部完成后一起放回调度器中
        """
        time.sleep(self._request_sleep_time)

        for request_middleware in self._request_middleware:
            request = request_middleware.transport(request)

        response = None
        retry_time = self.__chromesome.request_retry_time

        while (retry_time):
            try:
                response = request.fetch(self._request_timeout)
                break
            except (EXP.RequestConnectionError, EXP.RequestError, EXP.RequestTimeoutError, EXP.RequestTooManyRedirectsError) as e:
                self.recorder('ERROR', str(e))
                retry_time -= 1
                continue

        callback = request.callback
        rule = self.get_page_rule(request.rule_number)
        fid = request.fid
        associate = request.associate

        objs = getattr(self, callback)(request, response, rule, fid, associate) \
                   if callback else self.parse(request, response, rule, fid, associate)

        #迭代器判断
        if isinstance(objs, types.GeneratorType):
            for obj in objs:
                self._fetch_route(obj)
        elif objs == False:
            self.recorder('ERROR', 'Ignore URL[%s]' % request.url)
        else:
            self._fetch_route(objs)

    def _fetch_route(self, objs):
        if isinstance(objs, list):
            for obj in objs:
                self._fetch_obj(obj)
        else:
            self._fetch_obj(objs)

    def _fetch_obj(self, obj):
        if isinstance(obj, REQ.Request):
            self.master_push(obj)
        elif isinstance(obj, DT.Data):
            self.data_pipeline_push(obj)
        elif isinstance(obj, FILE.File):
            self.downloader_push(obj)

    def _local_request(self, request):
        """
        本机请求
        """
        if isinstance(request, REQ.Request):
            self.fetch_sync(request)
        else:
            raise TypeError('返回的不是Request对象')

    def _join(self):
        """
        等待pool中任务结束
        """
        self.__pool.join()

    def recorder(self, level, msg, *args, **kwargs):
        level = level.lower()
        getattr(self.__console_logger, level)(msg, *args, **kwargs)
        getattr(self.__file_logger, level)(msg, *args, **kwargs)

    def first_urls(self, first_urls):
        """
        定义爬取fisrt_urls的方式

        为了最大化的自由,实现具体爬虫时需要定义对first_url的处理方式
        可以将fisrt_url中url放入到scheduler中进行处理,也可以在本地由本机爬虫爬取
        需要本机爬去时,只需要返回request对象即可实现自动爬虫
        返回方式有return和yield两种,yield可以实现优先爬取,return等待所有request一起爬取
        """
        raise NotImplementedError('爬虫必须实现first_url方法')

    def parse(self, request, response):
        """
        response默认转发函数

        本机爬取得request在没有指定callback时默认转发到该函数
        request没有指定callback时,需要在子类中实现该方法
        """
        pass

    def start(self):
        """
        启动爬虫

        fisrt_urls中可以使用return和yield来进行返回Request对象,
        使用yield的时会优先处理别yield的请求，然后进行请求，直到当前深度到底会继续操作
        """
        self.recorder('INFO', '【%s】爬虫启动' % self.__name)

        requests = []
        first_urls = self.__chromesome.first_urls

        for first_url in first_urls:
            if isinstance(first_url, str):
                request = REQ.Request(first_url,headers = self._login_header)\
                                     .set_spider_name(self.__name)\
                                     .set_rule_number(self.__chromesome.first_rule_number)

            elif isinstance(fisrt_url, dict):
                request = REQ.Request.instance(**first_url).add_header(self._login_header)

            requests.append(request)

        return_or_yield = self.first_urls(requests)

        if isinstance(return_or_yield, types.GeneratorType):
            for r_or_y in return_or_yield:
                if isinstance(r_or_y, list):
                    for request in r_or_y:
                        self._local_request(request)
                        self.walk()
                else:
                    self._local_request(r_or_y)
                    self.walk()
        elif isinstance(return_or_yield, list):
            for request in return_or_yield:
                self._local_request(request)
            self.walk()
        else:
            self._local_request(return_or_yield)
            self.walk()

    def walk(self):
        scheduler_retry_time = self._scheduler_retry_time

        while scheduler_retry_time:
            request_json = self.scheduler_pull(self._scheduler_retry_interval)

            if not request_json:
                self.recorder('INFO', 'cheduler里没有request了,等待一会吧')
                scheduler_retry_time -= 1
                continue

            request = REQ.Request.instance(request_json)

            request.set_headers(self.__chromesome.login_header)
            self.fetch(request)

        self.merge_data()
        self.recorder('INFO', '爬取任务结束')

    def merge_data(self):
        """
        合并数据
        """
        self.recorder('INFO', '数据合并')

        merge_number = []
        upper_associate_stat = False
        merge_number_register = []

        #判断有关联关系的表
        for page_rule in self.__chromesome.iter_page_rule():
            if page_rule.scrawl_data_element and page_rule.associate:
                upper_associate_stat = True
                merge_number.append(page_rule.number)
            elif not page_rule.associate and page_rule.scrawl_data_element and upper_associate_stat:
                merge_number.append(page_rule.number)
                merge_number_register.append(merge_number)
                upper_associate_stat = False
                merge_number = []

        page_rule_len = len(self.__chromesome)
        merge_result_len = len(merge_number_register)
        data_pipelines = []

        #初始化collection对象
        for i in range(page_rule_len + merge_result_len):
            data_pipeline = PPL.generate_pipeline(**self.__chromesome.lasting)
            data_pipeline.select_db(self.__name)
            data_pipelines.append(data_pipeline)

        #从关联项的最后开始生成数据
        for idx_result, merge_number in enumerate(merge_number_register):
            lower_cursor = None
            collections = []
            merge_collection = None

            merge_collection_name = self._merge_data_collection + ('_%d' % idx_result)
            merge_collection = data_pipelines.pop().select_collection(merge_collection_name)

            for idx, number in enumerate(sorted(merge_number, reverse=True)):
                collection_name = self._middle_data_collection + ('_%d' % number)
                collection = data_pipelines.pop().select_collection(collection_name)

                if idx == 0:
                    lower_cursor = collection.find()
                else:
                    collections.append(collection)

            for doc in lower_cursor:
                full_data = {}
                fid = doc.get('fid')

                if fid:
                    del doc['fid']

                del doc['_id']
                del doc['_url']
                full_data = doc

                if fid:
                    for collection in collections:
                        if fid:
                            #只能查询到一条数据
                            doc = collection.find(filter={'_id': BS.ObjectId(fid)})

                            if doc.count():
                                doc = doc[0]
                                fid = doc.get('fid')

                                if fid:
                                    del doc['fid']

                                del doc['_id']
                                del doc['_url']
                                full_data = dict(full_data, **doc)

                merge_collection.insert(full_data)

                #import json
                #print json.dumps(full_data,ensure_ascii = False)

    def stop(self):
        pass

    def pause(self):
        #使用信号量使进程挂起，非阻塞
        pass

    def resume(self):
        #唤醒挂起进程
        pass

    def end(self):
        #下载器结束标识,将来会在管理里,downloader的生命周期为整个spider框架的生命周期
        self.__downloader.push(DL.DOWNLOADER_FINISH_FLAG)
        self.__pool.join()
        GEV.wait()

    def fetch_sync(self, request, **args):
        """
        阻塞访问request,用于必须确保完成的任务
        """
        self.recorder('INFO', '阻塞爬取地址【%s】' % request.url.encode('utf8'))
        self.fetch(request, **args)
        self._join()

    def fetch(self, request, **args):
        """
        非阻塞访问request
        """
        self.recorder('INFO', '非阻塞爬取地址【%s】' % request.url.encode('utf8'))
        self.__pool.spawn(self._fetch, request, **args)

    def master_push(self, request):
        """
        向master推送medium
        """
        #print request.json
        ret = self.__rpc.push(request.json)
        self.recorder('DEBUG','push进入request调度器[%s]' % ret)

    def data_pipeline_push(self, data):
        """
        向数据管道推送数据
        """
        for data_middleware in self._data_middleware:
            data = data_middleware.transport(data)

        rule_number = data.rule_number
        table_name = self._middle_data_collection + ('_%d' % rule_number)
        insert_id = self.__data_pipeline.insert(table_name, data=data())
        data.set_fid(insert_id)

    def downloader_push(self, file_obj):
        ret = self.__downloader.push(file_obj.json)
        self.recorder('DEBUG','push进入下载调度器[%s]' % ret)

    def scheduler_pull(self, timeout):
        """
        从调度器拉request_json
        """
        return self.__scheduler.pull(timeout)

    def get_page_rule(self, number):
        """
        获取当前的PageRule对象
        """
        return self.__chromesome.get_page_rule(number)

    def page_rule_parse(self, request, response, page_rule, fid):
        raise NotImplementedError('spider必须实现page_rule_parse方法')

    @property
    def name(self):
        return self.__name

    @property
    def chromesome(self):
        return self.__chromesome


class RuleLinkSpider(BaseSpider):
    def first_urls(self, requests):
        for request in requests:
            request.callback = 'first_parse'

        return requests

    def first_parse(self, request, response, rule, fid, associate):
        first_page_rule = rule
        requests = self.page_rule_parse(request, response, first_page_rule, fid, associate)
        return requests

    def parse(self, request, response, rule, fid, associate):
        requests = self.page_rule_parse(request, response, rule, fid, associate)
        return requests

    #返回一个Request对象，或者Request的对象列表,返回的Request自动发送到scheduler
    def page_rule_parse(self, requset, response, page_rule, fid, associate):
        """
        PageRule规则解析
        生成File放入downloader中下载
        生成Request,放入scheduler
        生成Data,自动放入数据管道中,进行存储(也可以为了效率采用批量的方式存储)
        """
        self.recorder('INFO', '规则号码【%d】' % (page_rule.number))

        dom = UTLC.response2dom(response)
        url = response.url
        headers = self._login_header
        cookies = response.cookies
        spider_name = self.name
        next_associate = page_rule.associate
        rule_number = page_rule.number
        next_rule_number = page_rule.next_number

        data_files = []
        datas = []
        requests = []
        next_page_requests = []

        #是否有下载的配置项
        #如果有就进行下载       
        #yield downloader
        #下载后的存储信息和data结合
        if page_rule.extract_file_element:
            data_files = EXT.FileExtractor(response,dom, url, page_rule.extract_file_element,spider_name=spider_name, cookies=cookies,headers=headers).extract()

        #数据抽取
        #如果上一规则为关联,数据中才记录fid
        if page_rule.scrawl_data_element:
            if associate:
                datas = EXT.DataExtractor(dom, url, page_rule.scrawl_data_element, fid=fid, rule_number=rule_number).extract()
            else:
                datas = EXT.DataExtractor(dom, url, page_rule.scrawl_data_element, rule_number=rule_number).extract()

        #只有数据和文件的数量相同时才能进行下载,否则没办法存储
        if datas and data_files:
            if len(data_files) != len(datas):
                raise TypeError('生成的数据和文件的数量不同没法下载')
            else:
                for idx_data, (data, file_obj) in enumerate(data_files):
                    datas[idx_data] = datas[idx_data] + data
                    yield file_obj
        elif not datas:
            for idx_data, (data, file_obj) in enumerate(data_files):
                datas.append(data)
                yield file_obj

        yield datas

        #应该在这里设置page_rule的number
        if page_rule.extract_url_type == PR.EXTRACT_URL_TYPE:
            requests = EXT.UrlExtractor(response, dom, url, page_rule.extract_url_element, spider_name, next_rule_number, fid, next_associate,
                                        cookies, headers).extract()

        elif page_rule.extract_url_type == PR.FORMAT_URL_TYPE:
            requests = EXT.UrlFormatExtractor(response,dom, url, page_rule.extract_url_element, spider_name, next_rule_number, fid, next_associate, cookies,
                                              headers).extract()
        elif page_rule.extract_url_type == PR.NONE_URL_TYPE:
            pass

        if page_rule.associate:
            #数据产生的量必须和后续url产生量相同,这样才可以关联数据和链接
            print len(datas),len(requests)
            if datas and requests:
                if len(datas) != len(requests):
                    raise TypeError('生成的数据数量和链接数量不同,无法建立关系')
                else:
                    for i_data, data in enumerate(datas):
                        requests[i_data].set_fid(data.fid)

        yield requests

        #下一页链接抽取和普通抽取的唯一区别是page_rule的number
        if page_rule.next_page_url_type == PR.EXTRACT_URL_TYPE:
            next_page_requests = EXT.UrlExtractor(response,dom, url, page_rule.next_page_url_element, spider_name, rule_number, fid, associate, cookies,
                                                  headers).extract()
        elif page_rule.next_page_url_type == PR.FORMAT_URL_TYPE:
            next_page_requests = EXT.UrlFormatExtractor(response,dom, url, page_rule.next_page_url_element, spider_name, rule_number, fid, next_associate,
                                                        cookies, headers).extract()
        elif page_rule.next_page_url_type == PR.NONE_URL_TYPE:
            pass

        yield next_page_requests

        self.recorder('DEBUG','下载文件数量[%d]\n抽取数据数量[%d]\n抽取链接数量[%d]\n抽取下一页链接数量[%d]' % (len(data_files), len(datas), len(requests), len(next_page_requests)))


# 广度优先策略找到终端目标页面，爬取最终数据
class BreadthFirstSpider(BaseSpider):
    def first_urls(self, requests):
        for request in requests:
            request.callback = 'page_rule_parse'
            yield request

    def __isLeafPage(self, responseContent, page_rule):

        leafFlag = page_rule['leaf_page']['leaf_flag']

        if leafFlag in responseContent:
            # print 'Found Leaf Page'
            return True
        else:
            return False

    def __leafPageHandle(self, dom, page_rule, request):
        routeXPathList = page_rule['leaf_page']['leaf_extract_regular']['leaf_route_path_extract']
        routePathStr = ""
        routePathList = None

        for xpathStr in routeXPathList:
            routePathList = dom.xpath(xpathStr)

            if len(routePathList) > 0:
                routePathStr = "_".join(routePathList)

        if routePathStr == "":
            self.recorder('ERROR', 'Can not find route path ERROR!!')
            return None

        leafURL = dom.xpath(page_rule['leaf_page']['leaf_extract_regular']['leaf_download_extract'])

        if len(leafURL) > 0:
            url_info = urlparse.urlparse(leafURL[0])

            if not url_info.scheme and not url_info.hostname:
                req_info = urlparse.urlparse(request.url)
                leafURL[0] = req_info.scheme + '://' + req_info.hostname + leafURL[0]

            self.recorder('INFO', 'Leaf-Page[%s] URL[%s]' % (routePathStr, leafURL[0]))

            file_name = hashlib.md5(leafURL[0]).hexdigest()
            routePathList.append(request.get_title())

            fileObj = FILE.File(leafURL[0], file_name, method=request.method, headers=request.headers, cookies=request.cookies, data=request.data)

            dataObj = DT.Data(node_route=routePathList, file_path=file_name)
            dataObj.rule_number = request.rule_number

            return [dataObj, fileObj]
        else:
            self.recorder('ERROR', "Can not find download URL ERROR!!")
            return None

    #  忽略掉 deny urls
    def __isDenyUrl(self, cur_url, page_url):

        for denyReg in page_url['content_filter']['deny_urls']:
            if re.match(denyReg, cur_url):
                return True

        return False

    #   忽略掉 invalid urls
    def __isInvalidUrl(self, cur_url, page_url):

        for validReg in page_url['content_filter']['valid_urls']:
            if re.match(validReg, cur_url):
                return False

        return True

    def page_rule_parse(self, request, response, page_rule, fid, associate):
        self.recorder('DEBUG', "get in BreadthFirstSpider for URL[%s][%s][%d]" % (request.url, request.get_title(), request.rule_number))

        dom = UTLC.response2dom(response)

        if dom == False:
            self.recorder('ERROR', 'HTML Parse to Dom ERROR!!')
            yield None
        else:
            if self.__isLeafPage(response.content, page_rule):
                downloadInfo = self.__leafPageHandle(dom, page_rule, request)

                time.sleep(1)
                yield downloadInfo
            else:
                url_list = dom.xpath('//a//@href|//a[normalize-space(text())!=\'\']/text()|//a/span/text()')

                # for url_content in url_list:
                #     self.log.debug('Content[%s]' % url_content)

                self.recorder('INFO', 'URL Count[%d]' % len(url_list))
                config_header = self.get_chromesome().login_header

                for i in range(0, len(url_list)):

                    if (i % 2) == 0:
                        cur_url = url_list[i]

                        if 'javascript' in cur_url:
                            cur_url = EXT.UrlSubstituteExtractor(page_rule).extract(cur_url, dom)
                            print 'Get extracted URL[%s]' % cur_url

                        if self.__isDenyUrl(cur_url, page_rule) or self.__isInvalidUrl(cur_url, page_rule):
                            self.recorder('INFO', 'Ignore URL[%s]' % cur_url)
                            continue

                        url_info = urlparse.urlparse(cur_url)

                        if not url_info.scheme and not url_info.hostname:
                            req_info = urlparse.urlparse(request.url)
                            cur_url = req_info.scheme + '://' + req_info.hostname + cur_url

                        if cur_url != request.url:
                            curRequest = REQ.Request(cur_url,
                                                     headers=config_header,
                                                     callback="page_rule_parse",
                                                     url_route=request.url_route,
                                                     title_route=request.title_route)

                            curRequest.set_spider_name(self.name)
                            curRequest.set_rule_number(request.rule_number + 1)
                            curRequest.add_url_route_element((url_list[i], url_list[i + 1]))

                            self.recorder('INFO',
                                          'URL[%s], Title[%s], Layer[%d]' % (cur_url, '->'.join(curRequest.title_route), request.rule_number + 1))

                            time.sleep(1)
                            yield curRequest
                        else:
                            #  直接忽略当前页自回访 url
                            pass

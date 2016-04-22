#*-*coding:utf8*-*
import re
import time
import copy
import types
import gevent as GEV
import gevent.pool as GEVP
import bson as BS

import Araneae.data as DT
import Araneae.dna.rule as PR
import Araneae.pipeline as PPL
import Araneae.scheduler as SCH
import Araneae.extractor as EXT 
import Araneae.net.request as REQ 
import Araneae.dna.chromesome as CHM 

from Araneae.utils.log import Plog


"""
`spider.py` -- 爬虫基类和个性化爬虫实现
=======================================
"""

class BaseSpider(object):
    """
    每个spider必备:
        +爬虫名,用来唯一标识一个爬虫
        +爬虫运行类型:#Singleton单机模式(不指定时默认为该模式),Distributed(分布式,需要启动master,所有功能都能使用)
        +一个chromesome,配置爬去规则
        +一个pool,用来爬取任务,pool的大小可以限制爬虫的速度
        +一个thread_id,每个爬虫都在一个thread中,用来管理该线程

        +一个scheduler,用来pull任务
        +一个data_pipeline,一个传输数据管道,根据配置爬虫情况(可选)
        +一个rpc对象,如果为单机模式,rpc关联到scheduler进行push,单机模式下功能退化,只能满足简单的爬虫功能(rpc对象必须有一个和scheduler相同的push接口)
    """
    __rpc = None
    __name = ''
    __pool = None
    __thread_id = 0
    __scheduler = None
    __chromesome = None
    __running_type = ''     
    __data_pipeline = None

    def __init__(self,chromesome):
        """
        初始化spider必要参数

        参数:
            chromesome:爬虫配置(必须为BaseChromesome子类)

        """
        if isinstance(chromesome,CHM.BaseChromesome):
            self.__chromesome = chromesome
        else:
            raise TypeError('参数必须为Chromesome类型')

        self.__name = chromesome.get('SPIDER_NAME')
        self.__running_type = chromesome.running_type

        self.__pool = GEVP.Pool(chromesome.getint('CONCURRENT_REQUESTS'))
        self.__scheduler = getattr(SCH,chromesome.scheduler)()

        if chromesome.running_type == CHM.RUNNING_TYPE_SINGLETON:
            self.__rpc = self.__scheduler
        elif chromesome.running_type == CHM.RUNNING_TYPE_DISTRIBUTED:
            #实例化rpc
            pass
                
        if chromesome.lasting:
            self.__data_pipeline = PPL.generate_pipeline(**chromesome.lasting)
            self.__data_pipeline.select_db(self.__name)

        self._scheduler_retry_time = self.__chromesome.getint('SCHEDULER_RETRY_TIME')
        self._scheduler_retry_interval = self.__chromesome.getint('SCHEDULER_RETRY_INTERVAL')

	self._request_timeout = self.__chromesome.getint('REQUEST_TIMEOUT')
	self._request_sleep_time = self.__chromesome.getint('REQUEST_SLEEP_TIME')

	self._login_header = self.__chromesome.getdict('LOGIN_HEADER')

    def first_urls(self,first_urls):
        """
        定义爬取fisrt_urls的方式

        为了最大化的自由,实现具体爬虫时需要定义对first_url的处理方式
        可以将fisrt_url中url放入到scheduler中进行处理,也可以在本地由本机爬虫爬取
        需要本机爬去时,只需要返回request对象即可实现自动爬虫
        返回方式有return和yield两种,yield可以实现优先爬取,return等待所有request一起爬取
        """
        raise NotImplementedError('爬虫必须实现first_url方法')

    def parse(self,response):
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
        Plog('【%s】爬虫启动' % self.__name)

        #构建first_urls的request对象
        first_urls = self.__chromesome.first_urls

        requests = []

        for first_url in first_urls:
            if isinstance(first_url,str):
                requests.append(REQ.Request(first_url,rule_number = self.__chromesome.first_rule_number,headers = self._login_header))
            elif isinstance(fisrt_url,dict):
                requests.append(REQ.json2request(first_url,rule_number = self.__chromesome.first_rule_number,headers = self._login_header))

        return_or_yield = self.first_urls(requests)

        if isinstance(return_or_yield,types.GeneratorType):
            for r_or_y in return_or_yield:
                if isinstance(r_or_y,list):
                    for request in r_or_y:
                        self._local_request(request)
                        self.walk()
                else:
                    self._local_request(r_or_y)
                    self.walk()
        elif isinstance(return_or_yield,list):
            for request in r_or_y:
                self._local_request(request)
            self.walk()
        else:
            self._local_request(return_or_yield)
            self.walk()

    def walk(self):
        while self._scheduler_retry_time:
            if not len(self.__scheduler):
                GEV.sleep(self._scheduler_retry_interval)
                self._scheduler_retry_time -= 1
                Plog('cheduler里没有request了,等待一会吧')
            else:
                self._scheduler_retry_time = self.__chromesome['SCHEDULER_RETRY_TIME']
                request_json = self.scheduler_pull()
                request = REQ.json2request(request_json)
                self.fetch(request)

        Plog('爬取任务结束')
        self.end()

    def merge_data(self):
        """
        合并数据
        """
        merge_number = []
        upper_associate_stat = False
        merge_number_register = []

        for page_rule in self.__chromesome.iter_page_rule():
            print page_rule.number
            if page_rule.scrawl_data_element and page_rule.associate:
                upper_associate_stat = True
                merge_number.append(page_rule.number)
                print merge_number
            elif not page_rule.associate and page_rule.scrawl_data_element and upper_associate_stat:
                merge_number.append(page_rule.number)
                print merge_number
                merge_number_register.append(merge_number)
                print merge_number_register
                upper_associate_stat = False
                merge_number = []

        page_rule_len = len(self.__chromesome)
        merge_result_len = len(merge_number_register)
        data_pipelines = []

        for i in range(page_rule_len+merge_result_len):
            data_pipeline = PPL.generate_pipeline(**self.__chromesome.lasting)
            data_pipeline.select_db(self.__name)
            data_pipelines.append(data_pipeline)
        
        for idx_result,merge_number in enumerate(merge_number_register):
            lower_cursor = None
            collections = []
            merge_collection = None

            merge_collection_name = self.__chromesome.merge_data_collection + ('_%d' % idx_result)
            merge_collection = data_pipelines.pop().select_collection(merge_collection_name)

            for idx,number in enumerate(sorted(merge_number,reverse = False)):
                collection_name = self.__chromesome.middle_data_collection + ('_%d' % number)
                collection = data_pipelines.pop().select_collection(collection_name)

                if idx == 0:
                    lower_cursor = collection.find()
                else:
                    collections.append(collection)

            for doc in lower_cursor:
                full_data = {}
                fid = doc.get('fid')
                del doc['_id']
                full_data = doc
                
                if fid:
                    for collection in collections:
                        if fid:
                            #不会查询到多条数据
                            doc = collection.find(filter = {'_id':BS.ObjectId(fid)})
                            if doc.count():
                                doc = doc[0]
                                fid = doc.get('fid')
                                del doc['_id']
                                del doc['fid']
                                full_data = dict(full_data,**doc)
                import json
                print '完整数据'          
                print json.dumps(full_data,ensure_ascii = False)

                

            
                        
    def stop(self):
         pass

    def pause(self):
        #使用信号量使进程挂起，非阻塞
        pass

    def resume(self):
        #唤醒挂起进程
        pass

    def end(self):
        self.__pool.join()

    def fetch_sync(self,request,**args):
        """
        阻塞访问request,用于必须确保完成的任务
        """
        Plog('阻塞爬取地址【%s】' % request.url.encode('utf8'))
        self.fetch(request,**args)
        self._join()

    def fetch(self,request,**args):
        """
        非阻塞访问request
        """
        Plog('非阻塞爬取地址【%s】' % request.url.encode('utf8'))
        self.__pool.spawn(self._fetch,request,**args)

    def master_push(self,request):
        """
        向master推送medium
        """
        print request.json
        self.__rpc.push(request.json)

    def data_pipeline_push(self,data):
        """
        向数据管道推送数据
        """
        if data.fid:
            data.add(**{'fid':data.fid})

        rule_number = data.rule_number
        table_name = 'Rule_%d' % rule_number
        insert_id = self.__data_pipeline.insert(table_name,data = data())
        data.fid = insert_id

    def scheduler_pull(self):
        """
        从调度器拉request_json
        """
        return self.__scheduler.pull()

    def get_page_rule(self,number):
        """
        获取当前的PageRule对象
        """
        return self.__chromesome.get_page_rule(number)

    @property
    def name(self):
        return self.__name

    @property
    def scheduler(self):
        return self.__scheduler

    def _fetch(self,request,**args):
        """
        完成访问的请求,并把response转发到回调函数
        回调函数中进行页面和数据解析,可以将解析的内容通过yield或者return的方式返回
        yield方式会立刻将request放回调度器中
        return方式会等待全部完成后一起放回调度器中
        """
        time.sleep(self._request_sleep_time)

        response = request.fetch(self._request_timeout)
        callback = request.callback
        rule = self.get_page_rule(request.rule_number)
        fid = request.fid

        request_or_datas = getattr(self,callback)(response,rule,fid) if callback else self.parse(response,rule,fid)

        if isinstance(request_or_datas,types.GeneratorType):
            #迭代生成器
            for r_or_d in request_or_datas:
                self._fetch_route(r_or_d)
        else:             
            self._fetch_route(request_or_datas)

    def _fetch_route(self,request_or_data):
        if isinstance(request_or_data,list):
            for r_or_d in request_or_data:
                self._fetch_request_or_data(r_or_d)
        else:
            self._fetch_request_or_data(request_or_data)
        
    def _fetch_request_or_data(self,request_or_data):
        if isinstance(request_or_data,REQ.Request):
            self.master_push(request_or_data)
        elif isinstance(request_or_data,DT.Data):
            self.data_pipeline_push(request_or_data)

    def _local_request(self,request):
        if isinstance(request,REQ.Request):
            self.fetch_sync(request)
        else:
            raise TypeError('返回的不是Request对象')
 
    def _join(self):
        self.__pool.join()


class RuleLinkSpider(BaseSpider):
    
    #起始url
    def first_urls(self,requests):
        self.merge_data()
        for request in requests:
            request.callback = 'first_parse'
            yield request
        
    def first_parse(self,response,rule,fid):
        first_page_rule = rule
        requests = self.page_rule_parse(response,first_page_rule,fid)
        return requests

    def parse(self,response,rule,fid):
        requests = self.page_rule_parse(response,rule,fid)
        return requests

    #返回一个Request对象，或者Request的对象列表,返回的Request自动发送到scheduler
    def page_rule_parse(self,response,page_rule,fid):
        """
        PageRule规则解析
        结果只有两个
        一个是生成Request,放入scheduler
        一个是生成Data,自动放入数据管道中,进行存储(也可以为了效率采用批量的方式存储)
        """
        print '规则号码'
        print page_rule.number
        print 'FID' 
        print fid
        #数据抽取规则
        datas = None
        requests = None

        if page_rule.scrawl_data_element:
            datas = EXT.DataExtractor(response,page_rule,fid)()
            yield datas
        
        print page_rule.extract_url_type
        #url抽取
        if page_rule.extract_url_type == PR.EXTRACT_URL_TYPE:
            print '通用url抽取'
            requests = EXT.UrlExtractor(response,page_rule,fid)()
        elif page_rule.extract_url_type == PR.FORMAT_URL_TYPE:
            requests = EXT.UrlFormatExtractor(response,page_rule,fid)()
        elif page_rule.extract_url_type == PR.NONE_URL_TYPE:
            pass

        print '链接生成数:%d' % len(requests)
        if page_rule.associate:
            #数据产生的量必须和后续url产生量相同,这样才可以关联数据和链接
            if datas and requests:
                if len(datas) != len(requests):
                    raise TypeError('生成的数据数量和链接数量不同,无法建立关系')
                else:
                    for i_data,data in enumerate(datas):
                        #print '数据fid:%s' %  data.fid
                        requests[i_data].fid = data.fid

        yield requests
        
        #是否有下载的配置项
        #如果有就进行下载       
        #yield downloader

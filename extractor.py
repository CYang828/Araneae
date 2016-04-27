#*-*coding:utf8*-*

import re
import itertools
import lxml.etree

import Araneae.data as DT
import Araneae.utils.http as UTLH
import Araneae.net.request as REQ
import Araneae.utils.setting as SET
import Araneae.utils.contrib as UTLC



"""
dom的生成过程可以通过cache进行优化，后续进行
"""

class BaseExtractor(object):
    __dom = None
    __response_url = ''

class UrlExtractor(BaseExtractor):
    """
    url抽取
    一个UrlExtractor只是针对一个response存在的,一个response对象可以对应有多个extractor
    """
    def __init__(self,spider_name,response,page_rule,fid = None):
        self.__spider_name = spider_name
        self.__response = response
        self.__rule = page_rule
        self.__dom = UTLC.response2dom(response)
        self.__response_url = response.url
        args = page_rule.extract_url_element
        self._allow_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(args.get('allow',[]))]
        self._deny_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(args.get('deny',[]))]
        self._headers = args.get('headers',{})
        self._cookies = args.get('cookies',{})
        self._method = args.get('method','GET')
        self._data = args.get('data',{})
        self._associate = False

        self._fid = fid

        self._urls = []
        self._allow_urls = []
        self._allow_requests = []
        self._extract_urls()
        self._extract_allow_urls()

    def __call__(self):
        self._url2request()
        return self._allow_requests
    
    def extract(self):
        return self._allow_urls

    def _extract_urls(self):
        self._urls = self.__dom.xpath('//a//@href')

    def _extract_allow_urls(self):
        """
        每一个url存在3种状态,deny(2) > allow(1) > unmark(0),在不同的情况下选择展现的url不同(这种代码量少,复杂度高)

        """
        #如果允许和阻止的规则都没有,则返回当前页面全部url
        if not self._allow_regexes and not self._deny_regexes:
            self._allow_urls = self._urls
            return
        
        #如果有阻止规则没有允许规则,则返回阻止规则剩下的全部url
        if not self._allow_regexes and self._deny_regexes:
            deny_list = []

            for idx,url in enumerate(self._urls):
                for deny_regex in self._deny_regexes:
                    if deny_regex.match(url):
                        deny_list.append(idx)
                        break

            for deny_idx in deny_list:
                del self._urls[deny_idx]

            #print 'DENY_LIST:' + str(deny_list)

            self._allow_urls = self._urls
            return 
            
        #如果允许和阻止的规则都有,则返回允许并不被阻止的url
        #如果有允许规则没有阻止规则,则返回允许规则的url
        #print '所有的url' 
        #print self._urls
        if self._allow_regexes and not self._deny_regexes:
            for idx,url in enumerate(self._urls):
                is_deny = False

                #先确定是否禁止
                for deny_regex in self._deny_regexes:
                    if deny_regex.match(url):
                        is_deny = True
                        #print 'DENY:' + url
                        break

                if not is_deny:                   
                    for allow_regex in self._allow_regexes:
                        if allow_regex.match(url):
                            #print 'ALLOW:' + url
                            self._allow_urls.append(url)
                            break
            
            return 

    def _url2request(self):
        #附加上次爬去后的cookies
        cookies = dict(self._cookies,**self.__response.cookies)

        request_args = {'method':self._method,'headers':self._headers,'cookies':cookies,'data':self._data,'fid':self._fid}

        for url in self._allow_urls:
            request = REQ.Request(UTLH.replenish_url(self.__response_url,url),**request_args).set_spider_name(self.__spider_name).set_rule_number(self.__rule.next_number).set_associate(self._associate)
            
            self._allow_requests.append(request)

    def set_associate(self,associate):
        self._associate = associate
        return self

    @property
    def urls(self):
        return self._urls

    @property
    def allow_urls(self):
        return self._allow_urls



class UrlFormatExtractor(BaseExtractor):
    """
    抽取格式化的url
    """

    def __init__(self,spider_name,response,page_rule,fid):
        self.__spider_name = spider_name
        self.__response = response
        self.__rule = page_rule
        self.__dom = UTLC.response2dom(response)
        self.__response_url = response.url

        args = page_rule.extract_url_element
        self._format_url = args.get('format_url')

        if not self._format_url:
            raise TypeError('format url配置中必须有format_url')

        #format_data中可以存在一些特殊的用法
        self._format_data = args.get('format_data')

        self._method = args.get('method','GET')
        self._data = args.get('data')
        self._headers = args.get('headers',None)
        self._cookies = args.get('cookies',None)

        self._fid = fid

        self._urls = []
        self._requests = []

        self._splice_urls()
        self._url2request()

    def __call__(self):
        return self._requests

    def _splice_urls(self):
        data_dict = {}

        if self._format_data:
            for key,formatter in self._format_data.items():
                #默认str为字符串
                if isinstance(formatter,(str,int)):
                    data_dict[key] = [formatter]
                elif isinstance(formatter,list):
                    data_dict[key] = formatter
                elif isinstance(formatter,dict):
                    dict_result = self._parse_formatter(formatter)
                    data_dict[key] = dict_result

        for format_data in self._yield_data(data_dict):
            #print self._format_url
            print format_data
            try:
                self._urls.append(self._format_url % format_data)
            except:
                raise TypeError('格式化url错误')
    
    def _yield_data(self,data_dict):
        product_data = []
        data_keys = data_dict.keys()

        for data_list in data_dict.values():
            product_data.append(data_list)

        for data in itertools.product(*product_data):
            yield_data_dict = {}

            for idx,key in enumerate(data_keys):
                yield_data_dict[key] = data[idx]

            yield yield_data_dict
              
    def _parse_formatter(self,formatter): 
        type = formatter.get('type','xpath')
        expression = formatter.get('expression')

        if not expression:
            raise TypeError('忘了写配置中的expression了')

        result = []

        if type == 'xpath':
            result = self.__dom.xpath(expression)
        elif type == 'css':
            result = self.__dom.cssselect(expression)

        return result

    def _url2request(self):
        cookies = combine(self._cookies,**self.__response.cookies)

        request_args = {'method':self._method,'headers':self._headers,'cookies':cookies,'data':self._data,'fid':self._fid}

        for url in self._urls:
            request = REQ.Request(UTLH.replenish_url(self.__response_url,url),**request_args).set_spider_name(self.__spider_name).set_rule_number(self.__rule.next_number)
            self._requests.append(request)

DEFAULT_TYPE = 'xpath'
DEFAULT_MULTIPLE = False

class DataExtractor(BaseExtractor):
    """
    数据抽取类
    抽取数据可以分为两种，一种mutiple 用于生成多个data对象,一种single 只生成单个data对象
    ?????????如何构建一个通用的数据抽取模型
    """
    def __init__(self,response,page_rule,fid = ''):
        self.__response = response
        self.__dom = UTLC.response2dom(response)
        self._extract_data_elements = page_rule.scrawl_data_element
        self._page_rule = page_rule

        self._parent_datas = {}
        self._datas = []
        self._fid = fid
       
        self._group_regex = re.compile(r'\[\?(\d*)\]')

        self._extract_data()

    def __call__(self,type = None):
        return self._datas

    def _extract_data(self):
        parent_datas = None

        for idx_element,element in enumerate(self._extract_data_elements):
            tp = element.get('type',DEFAULT_TYPE)
            expression = element.get('expression')

            parent = element.get('parent')
            multiple = element.get('multiple',DEFAULT_MULTIPLE)

            if not expression:
                raise TypeError('忘了写配置中的expression了')
            else:
                if not isinstance(expression,list):
                    expression = [expression]

            field = element.get('field')

            if not field:
                raise TypeError('忘了写配置中的field了')
            else:
                if not isinstance(field,list):
                    field = [field]

            middle = []

            if tp == 'xpath':
                for exp in expression:
                    results = self.__dom.xpath(exp)

                    for i_result,result in enumerate(results):
                        if isinstance(result,lxml.etree.ElementBase):
                            results[i_result] = result.text

                middle.append(results)
            elif tp == 'css':
                for exp in expression:
                    results = self.__dom.cssselect(exp)

                    for i_result,result in enumerate(results):
                        if isinstance(result,lxml.etree.ElementBase):
                            results[i_result] = result.text

                    middle.append(results)
            elif tp == 'group_xpath':
                group_expression = element.get('group_expression')
                
                if not group_expression:
                    raise TypeError('忘了写group_expression')

                if len(field) != len(expression):
                    raise TypeError('字段名称和expression必须一一对应')

                #结果寄存器
                #[ 
                #	{'xpath':[],'result':[[结果],...]},
                #	{'xpath':[],'result':[[结果],...]},
                #	...
                #]
                res_register = []

                for exp_idx,exp in enumerate(expression):
                    exps = []
                    group_flag = False
                    group_idx = None
                    res_register.append({'xpath':[],'result':[]})

                    group_match = self._group_regex.finditer(exp)

                    for match in group_match:
                        group_flag = True

                        group_idx = match.group(1)
                        print '匹配索引:' + group_idx

                        if group_idx.isdigit():
                            group_idx = int(group_idx)
                        else:
                            raise TypeError('不能识别的表达式')
                            
                        if group_idx >= exp_idx:
                            raise TypeError('组索引超出范围')
                        else:
                            sub_xpathes = []

                            #寄存器中已经存在该次产生的结果
                            if len(res_register[exp_idx]['xpath']):
                                for sub_xpath in res_register[exp_idx]['xpath']:
                                    for i_sub_xpath_num in range(len(res_register[group_idx]['xpath'])):
                                        for i_result in range(len(res_register[group_idx]['result'][i_sub_xpath_num])):
                                            sub_xpath = re.sub(self._group_regex,'[%d]' % (i_result + 1),sub_xpath)
                                            sub_xpathes.append(sub_xpath)    
                            else:
                                for i_sub_xpath_num in range(len(res_register[group_idx]['xpath'])):
                                    for i_result in range(len(res_register[group_idx]['result'][i_sub_xpath_num])):
                                        sub_xpath = re.sub(self._group_regex,'[%d]' % (i_result + 1),exp)
                                        print sub_xpath
                                        sub_xpathes.append(sub_xpath)    
                                
                            res_register[exp_idx]['xpath'] = sub_xpathes
                     
                    if not group_flag:
                        res_register[exp_idx]['xpath'] = [exp]
  
                    results = []

                    for xpath in res_register[exp_idx]['xpath']:
                        xpath = group_expression + xpath
                        result = self.__dom.xpath(xpath)

                        for i_res,res in enumerate(result):
                            if isinstance(res,lxml.etree.ElementBase):
                                result[i_res] = res.text

                        results.append(result) 
                                        
                    res_register[exp_idx]['result']  = results    

                import json
                #print json.dumps(res_register,ensure_ascii = False)

                #构造完整的数据,res_regiser中的result的顺序为文档查找顺序
                #url抽取也应该是文档查找顺序，这样才能对应上
                """
                最终构造的数据结构为
                {   
                    'field1':'data1',
                    'field2':'data2',
                    'field3':'data3',
                    ....
                }
                """
                register_len = len(res_register)
                middle = res_register[0]['result'][0]

                for i_field in range(register_len):
                    if i_field < register_len - 1:
                        middle_res = []

                        for i_mid,mid in enumerate(middle):
                            items = [item for item in itertools.product([mid],res_register[i_field+1]['result'][i_mid])]
                            middle_res += items
                            #print json.dumps(items,ensure_ascii = False)
                            #print '+++++++++++++++++++++++'
                        middle = middle_res


            #构造DATA
            datas = []
            raw_data = {}

            for mid in middle:
                for i_f,f in enumerate(field):
                    if multiple:
                        raw_data[f] = mid[i_f]
                    else:
                        if f not in raw_data.keys():
                            raw_data[f] = []
                            raw_data[f].append(mid[i_f])
                        else:
                            raw_data[f].append(mid[i_f])
                  
                if multiple:
                    data = DT.Data(**raw_data)
                    data.fid = self._fid
                    data.rule_number = self._page_rule.number
                    #print 'DATA'
                    #print json.dumps(raw_data,ensure_ascii = False)
                    datas.append(data)
                    raw_data = {}
            
            if not multiple:
                #print 'DATA'
                #print json.dumps(raw_data,ensure_ascii = False)
                #消除非multiple时field中只有一个
                for field,value in raw_data.items():
                    if len(value) == 1:
                        raw_data[field] = value[0]
                        
                data =  DT.Data(**raw_data)
                data.set_url(self.__response.url)
                data.fid = self._fid
                data.rule_number = self._page_rule.number
                datas.append(data)

            #关联parent
            if parent is not None:
                if parent == idx_element-1:
                    new_datas = []
                    for p_data in parent_datas:
                        for data in datas:
                            #print 'PARENT'
                            #print json.dumps(p_data(),ensure_ascii = False)
                            #print 'DATA'
                            #print json.dumps(data(),ensure_ascii = False)
                            new_data = p_data + data
                            new_data.set_url(self.__response.url)
                            new_datas.append(new_data)
                            #print 'NEW'
                            #print new_data

                    datas = new_datas

                else:
                    raise TypeError('parent必须是上一个field')

            parent_datas = datas

        self._datas = parent_datas

    def set_fid(self,fid):
        self._fid = fid
        return self

    @property
    def fid(self):
        return self._fid

   
    @fid.setter
    def fid(self,fid):
        self._fid = fid

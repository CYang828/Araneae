#*-*coding:utf8*-*

import re
import hashlib
import lxml.html
import itertools
import lxml.etree
import lxml.html.soupparser

import Araneae.file as FILE
import Araneae.data as DT
import Araneae.utils.http as UTLH
import Araneae.net.request as REQ
import Araneae.utils.setting as SET
import Araneae.utils.contrib as UTLC


class UrlExtractor(object):
    """
    url抽取
    dom:通过html生成的dom对象
    url:网页地址,用来补全url
    rule:抽取url的规则

    fid:上一次生成数据的id
    associate:生成的request是否与本页有关系
    spider_name:生成的request所属spider
    """
    def __init__(self,dom,url,rule,spider_name = '',rule_number = -1,fid = None,associate = False,cookies = {},headers = {}):
        self.__dom = dom
        self.__url = url
        self.__page_rule = rule
        
        self._allow_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(rule.get('allow',[]))]
        self._deny_regexes = [re.compile(regex,re.I) for regex in SET.revise_value(rule.get('deny',[]))]
        self._headers = rule.get('headers',{})
        self._cookies = rule.get('cookies',{})
        self._method = UTLH.validate_method(rule.get('method','GET'))
        self._data = rule.get('data',{})
        self._auth = rule.get('auth',{})
        self._proxies = rule.get('proxies',{})

        self._spider_name = spider_name
        self._associate = associate
        self._rule_number = rule_number
        self._fid = fid
        self._cookies = dict(self._cookies,**cookies)
        self._headers = dict(self._headers,**headers)

        self._urls = []
        self._allow_urls = []
        self._allow_requests = []

        self._extract_urls()
        self._extract_allow_urls()

    def _extract_urls(self):
        urls = self.__dom.xpath('//a//@href')
        self._urls = sorted(set(urls),key=urls.index)   

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
        request_args = {'method':self._method,'headers':self._headers,'cookies':self._cookies,'data':self._data,'fid':self._fid,'auth':self._auth,'proxies':self._proxies}

        for url in self._allow_urls:
            request = REQ.Request(UTLH.replenish_url(self.__url,url),**request_args).set_spider_name(self._spider_name).set_rule_number(self._rule_number).set_associate(self._associate)
            
            self._allow_requests.append(request)
  
    def extract(self):
        self._url2request()
        return self._allow_requests

    def set_spider_name(self,spider_name):
        self._spider_name = spider_name
        return self

    def set_fid(self,fid):
        self._fid = fid
        return self

    def set_rule_number(self,rule_number):
        self._rule_number = rule_number
        return self

    def set_associate(self,associate):
        self._associate = associate
        return self
    
    def add_cookies(self,cookies):
        self._cookies = dict(self._cookies,**cookies)
        return self

    def add_headers(self,headers):
        self._headers = dict(self._headers,**headers)
        return self

    @property
    def urls(self):
        return self._urls

    @property
    def allow_urls(self):
        return self._allow_urls

    @property
    def url(self):
        return self.__url


class UrlFormatExtractor(object):
    """
    抽取格式化的url
    """
    def __init__(self,dom,url,rule,spider_name = '',rule_number = -1,fid = None,associate = False,cookies = {},headers = {}):
        self.__dom = dom
        self.__url = url
        self.__rule = rule

        self._format_url = rule.get('format_url')

        if not self._format_url:
            raise TypeError('format url配置中必须有format_url')

        self._format_data = rule.get('format_data')

        self._headers = rule.get('headers',{})
        self._cookies = rule.get('cookies',{})
        self._method = UTLH.validate_method(rule.get('method','GET'))
        self._data = rule.get('data',{})
        self._auth = rule.get('auth',{})
        self._proxies = rule.get('proxies',{})

        self._spider_name = spider_name
        self._associate = associate
        self._fid = fid
        self._rule_number = rule_number

        self._cookies = dict(self._cookies,**cookies)
        self._headers = dict(self._headers,**headers)

        self._variable_regex = re.compile(r'(@[A-Za-z_]\w*)')
        #存储中间生成的变量结果
        self._middle_variables = {}
        self._middle_variables['@host_url'] = [self.__url]

        self._urls = []
        self._requests = []

        self._splice_urls()

    def _splice_urls(self):
        #存储最后构成url的结果
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
                    #print '名称'
                    #print key
                    if self._variable_regex.match(key):
                        #print '匹配'
                        self._middle_variables[key] = dict_result
                    else:
                        data_dict[key] = dict_result
                    #print '结果'
                    #print dict_result

        for format_data in self._yield_data(data_dict):
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
        elif type == 'constant':
            result = self._middle_variables[expression]
        elif type == 'function':
            iter_match = self._variable_regex.finditer(expression)

            for match in iter_match:
                variable_name = match.group(1)
                variable_value = str(self._middle_variables[variable_name])
                expression = expression.replace(variable_name,variable_value)
                
            #print expression
            result = eval(expression)

        return result

    def _url2request(self):
        request_args = {'method':self._method,'headers':self._headers,'cookies':self._cookies,'data':self._data,'fid':self._fid}

        for url in self._urls:
            request = REQ.Request(UTLH.replenish_url(self.__url,url),**request_args).set_spider_name(self._spider_name).set_rule_number(self._rule_number)
            self._requests.append(request)

    def extract(self):
        self._url2request()
        return self._requests

    def set_spider_name(self,spider_name):
        self._spider_name = spider_name

    def set_fid(self,fid):
        self._fid = fid

    def set_rule_number(self,rule_number):
        self._rule_number = rule_number

    def set_associate(self,associate):
        self._associate = associate

    def add_cookies(self,cookies):
        self._cookies = dict(self._cookies,cookies)
        return self

    def add_headers(self,headers):
        self._headers = dict(self._headers,headers)
        return self

    @property
    def urls(self):
        return self._urls


DEFAULT_TYPE = 'xpath'
DEFAULT_MULTIPLE = False

class DataExtractor(object):
    """
    数据抽取类
    """
    def __init__(self,dom,url,rule,fid = None,rule_number = -1):
        self.__dom = dom
        self.__url = url
        self.__rule = rule

        #用来知道存储在哪个库中
        self._rule_number = rule_number
        self._fid = fid

        self._datas = []
        self._group_regex = re.compile(r'\[\?(\d*)\]')

        self._extract_data()

    def _extract_data(self):
        parent_datas = None

        for idx_element,element in enumerate(self.__rule):
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
                    #print results
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
                        #print '匹配索引:' + group_idx

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
                            raw_data[f].append(mid)
                        else:
                            raw_data[f].append(mid)
                  
                if multiple:
                    data = DT.Data(**raw_data)
                    data.rule_number = self._rule_number
                    #print 'DATA'
                    #print json.dumps(raw_data,ensure_ascii = False)
                    datas.append(data)
                    raw_data = {}
            
            if not multiple:
                #import json
                #print 'DATA'
                #print json.dumps(raw_data,ensure_ascii = False)
                #消除非multiple时field中只有一个
                for field,value in raw_data.items():
                    if len(value) == 1:
                        raw_data[field] = value
                        
                data =  DT.Data(**raw_data) 
                data.rule_number = self._rule_number
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
                            new_datas.append(new_data)
                            #print 'NEW'
                            #print new_data

                    datas = new_datas

                else:
                    raise TypeError('parent必须是上一个field')

            parent_datas = datas

        self._datas = parent_datas

    def extract(self):
        for data in self._datas:
            data.set_url(self.__url)
                
            if self._fid:
                data.set_fid(self._fid)

        return self._datas

    def set_fid(self,fid):
        self._fid = fid
        return self

    def set_rule_number(self,rule_number):
        self._rule_number = rule_number
        return self

    @property
    def fid(self):
        return self._fid
   
    @fid.setter
    def fid(self,fid):
        self._fid = fid


class FileExtractor(UrlExtractor):

    def __init__(self,dom,url,rule,spider_name = '',rule_number = -1,fid = None,associate = False,cookies = {},headers = {}):
        self._field = rule.get('field')

        if not self._field:
            raise TypeError('下载文件必须有field字段')

        self._files = []

        super(FileExtractor,self).__init__(dom,url,rule,spider_name,rule_number,fid,associate,cookies,headers)

    def _url2file(self):
        file_args = {'method':self._method,'headers':self._headers,'cookies':self._cookies,'data':self._data,'fid':self._fid,'auth':self._auth,'proxies':self._proxies}

        for url in self._allow_urls:
            file_name = hashlib.md5(url).hexdigest()
            file_args['file_name'] = file_name
            file_obj = FILE.File(UTLH.replenish_url(self.url,url),**file_args)
            data = DT.Data(**{'%s_download'%self._field:file_name})
            
            self._files.append((data,file_obj))
       
    def extract(self):
        self._url2file()
        return self._files

if __name__ == '__main__':
    from requests import get
    import Araneae.utils.contrib as UTLC
    from collections import OrderedDict

    url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt2.action?currentBitCode=001001001001001001001'
    response = get(url)
    dom = UTLC.response2dom(response)
    rule =  {   
                'format_url':'%(url)s&pageSize=20&showPage=%(page)s',
                'format_data':OrderedDict(
                                [('url',{'type':'constant','expression':'@host_url'}),
                                ('@pages',{'type':'xpath','expression':r'//*[@id="ddd"]/nobr/select[1]/option[@*]/text()'}),
                                ('@max_page',{'type':'function','expression':'max(@pages)'}),
                                ('page',{'type':'function','expression':'range(2,@max_page+1)'})]
                              ),  
            }   

    url_fromat_extractor = UrlFormatExtractor(dom,url,rule) 
    #print url_fromat_extractor.urls

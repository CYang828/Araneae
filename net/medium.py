#*-*coding:utf8*-*

import json 

import Araneae.net.request as REQ

class Medium(object):
    """
    传输协议
    request:访问对象
    spider_name:调度器名称
    rule:当前request的页面规则序号
    field:索引filed名称
    fid:索引序号
    """
    def __init__(self,request,**args):
        if not isinstance(request,REQ.Request):
            raise TypeError('参数类型必须为Request')

        self._request = request
        self._rule = args.get('rule')
        self._field = args.get('field')
        self._fid = args.get('fid')

        self._json = ''
        self._json()

    @property
    def json(self):
        return self._json

    def _json(self):
        request_json = json.loads(request.json)       

        medium_json = {}
        medium_json['request'] = request_json
        medium_json['rule'] = self._rule

        if self._field and fid:
            medium_json['condition'] = {'fid':self._fid,'field':self._field}

        self._json = json.dumps(medium_json)

def request2medium(request,rule,field = '',fid = None):
    medium_args = {'rule':rule,'field':field,'fid':fid}

    medium = Medium(request,**medium_args)
    
    return medium

def requests2mediums(requests,rule,field = '',fid = None):
    mediums = []

    for request in requests:
        medium = request2medium(request,spider_name,rule,field,fid)
        mediums.append(medium)

    return mediums
    

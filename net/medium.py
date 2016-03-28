#*-*coding:utf8*-*

import json 

class Medium(self):
    """
    传输协议
    request:访问对象
    spider_name:调度器名称
    rule:当前request的页面规则序号
    field:索引filed名称
    fid:索引序号
    """
    def __init__(self,request,spider_name,rule,field = '',fid = 0):
        self._request = request
        self._spider_name = spider_name
        self._rule = rule
        self._field = field
        self._fid = fid

        self._json = ''
        self._json()

    @property
    def json(self):
        return self._json

    def _json(self):
        request_json = json.loads(request.json)       

        medium_json = {}
        medium_json['request'] = request_json
        medium_json['spider_name'] = self._spider_name
        medium_json['rule'] = self._rule

        if self._field and fid:
            medium_json['index'] = {'fid':self._fid,'field':self._field}

        self._json = json.dumps(medium_json)



# coding:utf8

import itertools
from collections import (OrderedDict,defaultdict)

from araneae.utils.python import arg_to_iter
from araneae.constant import (TREE_DATA_CHILD_PREFIX,TREE_DATA_PARENT_REGEX)
from araneae.utils.extractor import response_to_selector


class DataExtractor(object):
    """数据抽取器"""

    _child_prefix_len = len(TREE_DATA_CHILD_PREFIX)

    def __init__(self, regulations):
        self.regulations = arg_to_iter(regulations)

    def get_selector(self, selector, rgl):
        """获取selector对象"""

        assert rgl.get('type'), 'Extract data regulation must have `type` key'
        assert rgl.get('expression'), 'Extract data regulation must have `expression` key'

        t = rgl.get('type')
        e = rgl.get('expression')

        return {'xpath':lambda s,e: s.xpath(e),
                'css':lambda s,e: s.css(e),
                're':lambda s,e: s.re(e)}[t](selector, e)

    def extract_raw_data(self, response, regulation, recursion=False):
        """返回的raw data都是iter
        raw data格式[{field:data},{},...]"""

        selector = response.selector

        assert regulation.get('type'), 'Extract data regulation must have `type` key'
        
        t = regulation.get('type')
        raw_data = []

        if t == 'func':
            raw_data = self._func_parse(regulation)
        elif t == 'tree' and not recursion:
            raw_data = self._tree_parse(selector, regulation)
        elif t == 'table' and not recursion:
            pass
        else:
            raw_data = self._sel_parse(selector, regulation)

        return raw_data

    def _parse_regulations(self, response):
        """多条规则解析"""

        all_raw_data = []

        for irgl, regulation in enumerate(self.regulations):
            raw_data = self.extract_raw_data(response, regulation)
            p = regulation.get('parent', False)
            
            if p >= 0 and p < irgl:
                raw_data = [dict(pd,**d) for pd in all_raw_data[p] for d in raw_data]
                all_raw_data[p] = None
            
            all_raw_data.append(raw_data)

        return all_raw_data

    def _sel_parse(self, selector, rgl):
        """selector解析"""

        assert rgl.get('field'), 'Extract data regulation must have `field` key'
        f = rgl.get('field')
        m = rgl.get('mulrecord', False)

        selector = self.get_selector(selector, rgl) 
        data = selector.extract() if hasattr(selector, 'extract') else selector
        return [{f:d} for d in data] if m else arg_to_iter({f:data})

    def _func_parse(self, rgl):
        """函数数据解析"""

        assert rgl.get('expression'), 'Extract data regulation must have `expression` key'
        assert rgl.get('field'), 'Extract data regulation must have `field` key'
        e = rgl.get('expression')
        f = rgl.get('field')
        m = rgl.get('mulrecord', False)

        data = []

        if isinstance(e, six.string_types):
            data = arg_to_iter(eval(expression))
        elif hasattr(e, '__call__'):
            data = arg_to_iter(e())
        elif isinstance(e, list):
            data = arg_to_iter(e)
        
        return [{f:d} for d in data] if m else [].append({f:data})

    def _tree_parse(self, selector, regulation):
        """树状结构解析"""

        childs = {k:v for k,v in regulation.iteritems() if k.startswith(TREE_DATA_CHILD_PREFIX)}
        assert len(childs), 'Extract tree data must have `{}` prefix key'.format(TREE_DATA_CHILD_PREFIX)
        childs = OrderedDict(sorted(childs.items(), key=lambda x:int(x[0][self._child_prefix_len:])))

        expression_register = OrderedDict()
        result_register = defaultdict(list)
        field_register = []

        #树形结构数据构造
        for k,v in childs.iteritems():
            assert v.get('expression'), 'Extract tree data must have `expression` key'
            assert v.get('field'), 'Extract tree data must have `field` key'

            e = arg_to_iter(v.get('expression'))
            f = v.get('field')
            iuk = childs.keys().index(k)-1
            
            if iuk >= 0:
                uk = childs.keys()[iuk]
                e = [TREE_DATA_PARENT_REGEX.sub(str(x), em) for em in e for c in result_register[uk] for x in range(1, len(c)+1)]
            
            for me in e:
                vm = v
                vm['expression'] = me
                rm = self.get_selector(selector, vm)
                result_register[k].append(rm.extract())

            expression_register[k] = e
            field_register.append(f)
        
        #数据和字段合并
        data = []       
        raw_data = []

        for ir in range(len(childs)-1):
            cd, nd = data if data else result_register[childs.keys()[ir]], result_register[childs.keys()[ir+1]]

            for icd, scd in enumerate(cd):
                snd = nd[icd]

                if snd:
                    data = [x for x in itertools.product(arg_to_iter(scd), snd)]
        
        for di in data:
            dt = {}

            for fi,f in enumerate(field_register):
                dt[f] = di[fi]
            raw_data.append(dt)

        return raw_data       
        
    def _table_parse(self, selector, regulation):
        """表格状数据解析"""

        pass

    def extract(self, response):
        """抽取"""

        all_raw_data = self._parse_regulations(response)
        return [data for raw_data in all_raw_data if raw_data for data in raw_data]
        
 
    def extract_data(self, response):
        pass              
        
    



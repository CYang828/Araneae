# coding:utf8

from collections import (OrderedDict,defaultdict)

from Araneae.constant import (TREE_DATA_CHILD_PREFIX,TREE_DATA_PARENT_REGEX)
from Araneae.uitls.python import arg_to_iter
from Araneae.utils.extractor import response_to_selector


class DataExtractor(object):
    """数据抽取器"""

    def __init__(self, regulations=None):
        self._child_prefix_len = len(TREE_DATA_CHILD_PREFIX)
        self.regulations = arg_to_iter(regulations)

    def get_selector(self, selector, rgl):
        assert rgl.get('type'), 'Extract data regulation must have `type` key'
        assert rgl.get('expression'), 'Extract data regulation must have `expression` key'

        t = rgl.get('type')
        e = rgl.get('expression')

        return {'xpath':lambda s,e: s.xpath(e),
                'css':lambda s,e: s.xpath(e),
                're':lambda sme: s.xpath(e)}[t](selector, e)


    def extract_raw_data(self, response, regulation, recursion=False):
        """返回的raw data都是iter
        raw data格式[{field:data},{},...]"""

        selector = response_to_selector(response)

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

    def _sel_parse(self, selector, rgl):
        assert rgl.get('field'), 'Extract data regulation must have `field` key'
        f = rgl.get('field')
        m = rgl.get('mulrecord', False)

        data = self.get_selector(selector, rgl).extract()

        return [{f:d} for d in data] if m else [].append({f:data})

    def _func_parse(self, rgl):
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
        else isinstance(e, list):
            data = arg_to_iter(e)
        
        return [{f:d} for d in data] if m else [].append({f:data})

    def _tree_parse(self, selector, regulation):
        assert regulation.get('root'), 'Extract tree data must have `root` key'
        root = regulation.get('root')

        childs = {k:v for k,v in regulation.iteritems() if key.startswith(CHILD_PREFIX)]
        assert len(leafs), 'Extract tree data must have `{}` prefix key'.format(TREE_DATA_CHILD_PREFIX)
        
        childs = OrderedDict(sorted(childs.items(), key=lambda x:int(x[0][self._child_prefix_len():])))
        root = self.get_selector(selector, root)

        assert len(root), 'Extract tree root just have only one'

        expression_register = OrderedDict()
        result_register = defaultdict(list)
        field_register = OrderedDict()

        for k,v in leafs.iteritems():
            assert v.get('expression'), 'Extract tree data must have `expression` key'
            assert v.get('field'), 'Extract tree data must have `field` key'

            e = arg_to_iter(v.get('expression'))
            f = v.get('field')
            uk = leafs.keys().index(k)-1
        
            if uk >= 0:
                e = [TREE_DATA_PARENT_REGEX.sub(c, e) for c in range(len(result_register[uk]))]
            
            for me in e:
                vm = v
                vm['expression'] = me
                rm = get_selector(selector, vm)
                result_register[k].append(rm.extract())              
            
            expression_register[k] = e
            field_register[k] = f

       

        
        
        
    def _table_parse(self, selector, regulation):
        pass

    def extract_data(self, response):
        selector = response_to_selector(response)
               
        
    



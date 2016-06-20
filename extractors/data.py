# coding:utf8

from collections import (OrderedDict,defaultdict)

from Araneae.constant import LEAF_PREFIX
from Araneae.uitls.python import arg_to_iter
from Araneae.utils.extractor import response_to_selector


class DataExtractor(object):
    """数据抽取器"""

    def __init__(self, regulations=None):
        self._leaf_prefix_len = len(LEAF_PREFIX)
        self.regulations = arg_to_iter(regulations)

    def get_selector(self, selector, rgl):
        assert rgl.get('type'), 'Extract data regulation must have `type` key'
        assert rgl.get('expression'), 'Extract data regulation must have `expression` key'
        
        t = rgl.get('type')
        e = rgl.get('expression')

        return {'xpath':lambda s,e: s.xpath(e),
                'css':lambda s,e: s.xpath(e),
                're':lambda sme: s.xpath(e)}[t](selector, e)

    def get_raw_data(self, selector, regulation, recursion=False):
        """返回的raw data都是iter"""

        assert regulation.get('type'), 'Extract data regulation must have `type` key'
        assert regulation.get('expression'), 'Extract data regulation must have `expression` key'
        
        t = regulation.get('type')
        e = regulation.get('expression')
        f = regulation.get('field')
        raw_data = []

        if t == 'func':
            raw_data = self._func_parse(expression)
        elif t == 'tree' and not recursion:
            raw_data = self._tree_parse(selector, regulation)
        elif t == 'table' and not recursion:
            pass
        else:
            raw_data = get_selector(selector, t, e).extract()

        return raw_data

    def _func_parse(self, expression):
        data = []

        if isinstance(expression, six.string_types):
            data = arg_to_iter(eval(expression))
        elif hasattr(e, '__call__'):
            data = arg_to_iter(expression())
        else isinstance(e, list):
            data = arg_to_iter(expression)

        return data

    def _tree_parse(self, selector, regulation):
        assert regulation.get('root'), 'Extract tree data must have `root` key'
        root = regulation.get('root')

        leafs = {k:v for k,v in regulation.iteritems() if key.startswith(LEAF_PREFIX)]
        assert len(leafs), 'Extract tree data must have `{}` prefix key'.format(LEAF_PREFIX)
        
        leafs = OrderedDict(sorted(leafs.items(), key=lambda x:int(x[0][self._leaf_prefix_len():])))
        root = self.get_selector(selector, root)

        assert len(root), 'Extract tree root just have only one'

        expression_register = defaultdict()
        result_register = defaultdict()
        
        for k,v in leafs.iteritems():
            assert regulation.get('expression'), 'Extract tree data must have `expression` key'
            
            #根据正则,生成对应关系的xpath
            expression_register[k] = v['expression']
            result_register[k] = self.get_selector(selector, v))
             

    def _table_parse(self, selector, regulation):
        pass

    def extract_data(self, response):
        selector = response_to_selector(response)
               
        
    



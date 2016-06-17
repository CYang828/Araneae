# coding:utf8

from Araneae.uitls.python import arg_to_iter
from Araneae.utils.extractor import response_to_selector


class DataExtractor(object):

    def __init__(self, regulations=None):
        self.regulations = arg_to_iter(regulations)


    def get_raw_data(self, selector, regulation):
        """返回的raw data都是iter"""

        assert regulation.get('type'), 'Extract data regulation must have `type` key'
        assert regulation.get('expression'), 'Extract data regulation must have `expression` key'
        
        t = regulation.get('type')
        e = regulation.get('expression')
        raw_data = []

        if t == 'xpath':
            raw_data = selector.xpath(e).extract()
        elif t == 'css':
            raw_data = selector.css(e).extract()
        elif t == 're':
            raw_data = selector.re(e).extract()
        elif t == 'func':
            if isinstance(e, six.string_types):
                raw_data = arg_to_iter(eval(e))
            elif hasattr(e, '__call__'):
                raw_data = arg_to_iter(e())
            else isinstance(e, list):
                raw_data = arg_to_iter(e)

        return raw_data

    def _parse_regulations(self, selector):
        for rg in self.regulations:
            assert rg.get('field'), 'Extract data regulation must have `field` key'

            f = rg.get('field')
            m = rg.get('multiline', False)
            p = rg.get('parent')
                
            rwd = self.get_raw_data(selector, rg)
           
            
            
    def extract_data(self, response):
        selector = response_to_selector(response)
        
        
    



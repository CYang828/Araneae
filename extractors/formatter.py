# coding:utf8

import six

from Araneae.utils.python import arg_to_iter
from Araneae.utils.extractor import response_to_selector


class LinkFormatter(object):

    def __init__(self, formatter=None, prepare_variable=None, padding=None, link_filter=None, process_value=None, 
                 unique=None, canonicalize=True, data_extractor=None):
        self.data_extractor = data_extractor
        self.formatter = formatter
        self.prepare_variable = prepare_variable
        self.padding = padding
        self.link_filter = link_filter
        self.process_value = process_value

    def _prepare(self, selector):
        """vexp结构 ('xpath | css | re | func','')"""

        for key,vexp in self.prepare_variable.iteritems():
            t, e = vexp
            
            if t == 'xpath':
                selector.xpath(e)
            elif t == 'css':
                selector.css(e)
            elif t == 're':
                selector.re(e)
            elif t == 'func':
                if isinstance(e, six.string_types):
                    eval(e)
                elif hasattr(e, '__call__'):
                    e()
            

    def extract_links(self, response):
        selector = response_to_selector(response)
        
      


class LinkFormatterExtractor(LinkFormatter):
    pass

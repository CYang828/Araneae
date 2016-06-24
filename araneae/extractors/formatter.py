# coding:utf8

import six

from araneae.utils.python import arg_to_iter
from araneae.utils.extractor import response_to_selector


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
        pass 

    def extract_links(self, response):
        selector = response.selector

       
class LinkFormatterExtractor(LinkFormatter):
    pass

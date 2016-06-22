# coding:utf8

from araneae.rules import Rule
from araneae.utils.python import arg_to_iter
from araneae.extractors.data import DataExtractor

class ChainRule(Rule):
    """定义每页的规则项"""

    @classmethod
    def from_settings(cls, settings):
        ext_data_setting = settings['extract_data'] 
        ext_data_obj = DataExtractor(ext_data_setting)

        ext_request_setting = settings['extract_url']

        ext_next_request_setting = settings['extract_next_url']

        fmt_request_setting = settings['format_url']

        fmt_next_request_setting = settings['format_next_url']
    

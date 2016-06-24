# coding:utf8

from araneae.utils.python import arg_to_iter
from araneae.extractors.data import DataExtractor

class ChainRule(object):
    """定义每页的规则项,对外提供抽取器"""

    def __init__(self, data_extractor,request_extractor,format_request_extractor,next_request_extractor,format_next_request_extractor,file_request_extractor):
        self.data_extractor = data_extractor
        self.request_extractor = request_extractor
        self.format_request_extractor = format_request_extractor
        self.next_request_extractor = next_request_extractor
        self.format_next_request_extr = format_next_request_extractor
        self.file_request_extractor = file_request_extractor

    @classmethod
    def from_settings(cls, settings):
        data_extractor = None
        ext_data_setting = settings.get('extract_data')
        if ext_data_setting:
            data_extractor = DataExtractor(ext_data_setting) 

        request_extractor = None
        ext_request_setting = settings.get('extract_url')
        if ext_request_setting:
            request_extractor = None

        format_request_extractor = None
        fmt_request_setting = settings.get('format_url')
        if fmt_request_setting:
            format_request_extractor = None

        next_request_extractor = None
        ext_next_request_setting = settings.get('extract_next_url')
        if ext_next_request_setting:
            next_request_extractor = None

        format_next_request_extractor = None
        fmt_next_request_setting = settings.get('format_next_url')
        if fmt_next_request_setting:
            format_next_request_extractor = None

        file_request_extractor = None
        ext_file_request_setting = settings.get('extract_file_url')
        if ext_file_request_setting:
            file_request_extractor = None

        return cls(data_extractor, request_extractor, format_request_extractor, next_request_extractor,format_next_request_extractor, file_request_extractor)



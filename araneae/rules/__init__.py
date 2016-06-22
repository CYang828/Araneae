# coding:utf8

class Rule(object):

    def __init__(self, request_extractor, file_request_extractor, next_request_extractor, data_extractor):
        self.request_extractor = request_extractor
        self.file_request_extractor = file_request_extractor
        self.next_request_extractor = next_request_extractor
        self.data_extractor = data_extractor

    def request_extractor(self):
        return self.request_extractor

    def file_request_extractor(self):
        return self.file_request_extractor

    def next_request_extractor(self):
        return self.next_request_extractor

    def data_extractor(self):
        return self.data_extractor

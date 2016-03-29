#*-*coding:utf8*-*

#0:没有,1:抽取url,2:格式化                                                                                                                                     
NONE_URL_TYPE = 0
EXTRACT_URL_TYPE = 1
FORMAT_URL_TYPE = 2

class PageRule(object):
    """
    页面规则,用来确定输出的url和data
    """
    __extract_url_type = NONE_URL_TYPE
    __extract_url_element = None
    __extract_data_element = None
    __extract_data_field = ''

    def __init__(self,map):
        self._essential(map)

    def _essential(self,map):
        """
        在一个PageRule中,extract_urls和format_urls只能存在一个,如果两个同时存在,则抛弃format_urls(该方案以后可以进行调整)
        """
        if 'extract_urls' in map.keys():
            self.__extract_url_type = EXTRACT_URL_TYPE
            self.__extract_url_element = map['extract_urls']
        elif 'format_urls' in map.keys():
            self.__extract_url_type  = FORMAT_URL_TYPE
            self.__extract_url_element = map['format_urls']
        else:
            raise TypeError('PageRule中必须存在extract_urls或者format_urls中的一个')

        if 'extract_data' in map.keys():
            self.__extract_data_field = map['extract_data']['field']
            self.__extract_data_element = {'type':map['extract_data']['type'],'expression':map['extract_data']['expression']}

    @property
    def extract_url_type(self):
        return self.__extract_url_type

    @property
    def extract_url_element(self):
        return self.__extract_url_element

    @property
    def scrawl_data(self):
        return self.__extract_data_element

    @property
    def field(self):
        return self.__extract_data_field

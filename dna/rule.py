#*-*coding:utf8*-*

#0:没有,1:抽取url,2:格式化                                                                                                                                     
NONE_URL_TYPE = 0
EXTRACT_URL_TYPE = 1
FORMAT_URL_TYPE = 2

class PageRule(object):
    """
    页面规则,用来确定输出的url和data
    """
    __number = None
    __extract_url_type = NONE_URL_TYPE
    __extract_url_element = None
    __scrawl_data_element = None
    __fields = set([])

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
        #else:
        #    raise TypeError('PageRule中必须存在extract_urls或者format_urls中的一个')

        if 'extract_data' in map.keys():
            if isinstance(map['extract_data'],dict):
                self.__scrawl_data_element = [map['extract_data']]
            elif isinstance(map['extract_data'],list):
                self.__scrawl_data_element = map['extract_data']

            for data_item in self.__scrawl_data_element:
                if 'field' in data_item.keys():
                    if isinstance(data_item['field'],list):
                        for f in data_item['field']:
                            if f in self.__fields:
                                raise TypeError('同一spider中不能出现重复field')
                            else:
                                self.__fields.add(f)
                    else:
                        if data_item['field'] in self.__fields:
                                raise TypeError('同一spider中不能出现重复field')
                        else:
                            self.__fields.add(data_item['field'])
    @property
    def fields(self):
        return self.__fields    
        
    @property
    def extract_url_type(self):
        return self.__extract_url_type

    @property
    def extract_url_element(self):
        return self.__extract_url_element

    @property
    def scrawl_data_element(self):
        return self.__scrawl_data_element

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self,rule):
        self.__number = rule

    

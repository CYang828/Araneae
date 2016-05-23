#*-*coding:utf8*-*

#0:没有,1:抽取url,2:格式化
NONE_URL_TYPE = 0
EXTRACT_URL_TYPE = 1
FORMAT_URL_TYPE = 2


class PageRule(object):
    """
    页面规则,用来确定输出的url和data
    """

    def __init__(self, map):
        self.__number = None
        self.__extract_url_type = NONE_URL_TYPE
        self.__extract_url_element = None
        self.__extract_file_element = None
        self.__next_page_url_type = NONE_URL_TYPE
        self.__next_page_url_element = None
        self.__scrawl_data_element = None
        self.__associate = False
        self.__fields = set([])
        self.__next_number = None

        self._essential(map)

    def _essential(self, map):
        """
        在一个PageRule中,extract_urls和format_urls只能存在一个,如果两个同时存在,则抛弃format_urls(该方案以后可以进行调整)
        """
        if 'extract_urls' in map.keys():
            self.__extract_url_type = EXTRACT_URL_TYPE
            self.__extract_url_element = map['extract_urls']
        elif 'format_urls' in map.keys():
            self.__extract_url_type = FORMAT_URL_TYPE
            self.__extract_url_element = map['format_urls']

        if 'extract_files' in map.keys():
            self.__extract_file_element = map['extract_files']

        if 'extract_next_page' in map.keys():
            self.__next_page_url_type = EXTRACT_URL_TYPE
            self.__next_page_url_element = map['extract_next_page']

        elif 'format_next_page' in map.keys():
            self.__next_page_url_type = FORMAT_URL_TYPE
            self.__next_page_url_element = map['format_next_page']

        if 'extract_data' in map.keys():
            if isinstance(map['extract_data'], dict):
                self.__scrawl_data_element = [map['extract_data']]
            elif isinstance(map['extract_data'], list):
                self.__scrawl_data_element = map['extract_data']

            if self.__scrawl_data_element[len(self.__scrawl_data_element) - 1].get('associate'):
                self.__associate = True

            for data_item in self.__scrawl_data_element:
                if 'field' in data_item.keys():
                    if isinstance(data_item['field'], list):
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

    def set_number(self, number):
        self.__number = number
        return self

    @property
    def next_number(self):
        return self.__next_number

    @next_number.setter
    def next_number(self, next_number):
        self.__next_number = next_number

    @property
    def fields(self):
        return self.__fields

    @property
    def extract_url_type(self):
        return self.__extract_url_type

    @property
    def next_page_url_type(self):
        return self.__next_page_url_type

    @property
    def next_page_url_element(self):
        return self.__next_page_url_element

    @property
    def extract_url_element(self):
        return self.__extract_url_element

    @property
    def extract_file_element(self):
        return self.__extract_file_element

    @property
    def scrawl_data_element(self):
        return self.__scrawl_data_element

    @property
    def associate(self):
        return self.__associate

    @property
    def number(self):
        return self.__number

    @number.setter
    def number(self, rule):
        self.__number = rule

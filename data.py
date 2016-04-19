#*-*coding:utf8*-*

import json

class Data(object):
    __kv = {}
    __fid = []

   
    def __init__(self,**kvargs):
        """
        kvargs为数据内容
        """
        self.__kv = kvargs

    def __get__(self,data):
        pass

    def __add__(self,data):
        tmp_kv = {}

        for field in data.fields:
            #如果data有同一field
            if field in self.fields:
                tmp_value = self.__kv[field]

                if isinstance(tmp_value,list):
                    tmp_value.append(data.value[field])
                else:
                    tmp_value = [tmp_value]
                    tmp_value.append(data.value[field])
            
                tmp_kv[field] = tmp_value
            else:
                tmp_kv = dict(self.__kv,**data())

        return Data(**tmp_kv)

    def __call__(self):
        return self.__kv

    def __str__(self):
        return json.dumps(self.__kv,ensure_ascii = False).encode('utf8')

    @property
    def fields(self):
        return self.__kv.keys()

    @property
    def fid(self):
        return self.__fid

    @fid.setter
    def fid(self,fid):
        self.__fid = fid

    @property
    def value(self):
        return self.__kv

    @value.setter
    def value(self,value):
        self.__kv = value

if __name__ == '__main__':        
    pass
        

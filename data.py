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

    def parent(self,data,parent_field = None):
        """
        field名称不可以重复
        """
        if not parent_field:
            self.__kv['__sub'] = data.value
        else:
            self._find_sub(self.__kv,parent_field,data)
            
        return self.__kv

    def _find_sub(self,kv,parent_field,data):
        if parent_field in kv.keys():
            kv['__sub'] = data.value
        else:
            if '__sub' in kv.keys():
                self._find_sub(kv['__sub'],parent_field,data)
            else:
                return None

    def __add__(self,data):
        for field in data.field:
            #如果data有同一field
            if field in self.field:
                tmp_value = self.__kv[field]

                if isinstance(tmp_value,list):
                    tmp_value.append(data.value[field])
                else:
                    tmp_value = [tmp_value]
                    tmp_value.append(data.value[field])
                    print tmp_value
            
                self.__kv[field] = tmp_value
            else:
                self.__kv = dict(self.__kv,**data())

        return self

    def __call__(self):
        return self.__kv

    def __str__(self):
        return json.dumps(self.__kv,ensure_ascii = False)

    @property
    def field(self):
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
    a = Data(subject = '语文',__sub = {'grade':'chinese'})
    b = Data(name = '试卷')
    c = a.parent(b,'grade')
    print c

        

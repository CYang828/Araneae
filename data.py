#*-*coding:utf8*-*

class Data(object):
    __kv = {}
    __fid = None

    def __init__(self,**kvargs):
        self.__kv = kvargs

    def __call__(self):
        return self.__kv

    @property
    def fid(self):
        return self.__fid

    @fid.setter
    def fid(self,fid):
        self.__fid = fid
                

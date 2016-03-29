#*-*coding:utf8*-*

class Data(object):
    __data = None
    __field = ''

    def __init__(self,data,field):
        self._data = data
        self._field = field

    @property
    def data(self):
        return self._data

    @property
    def field(self):
        return self._field


#*-*coding:utf8
import dupefilter

class BaseRPC(Object):

    __dupefilter = None
    __scheduler = None

    def push(self,request):
        raise NotImplementedError('RPC对象必须实现push方法')

    @property
    def dupefilter(self):
        return self.__dupefilter

class SingletonRPC(BaseRPC):

    def __init__(self):
        self.__dupefilter = dupefilter.SingletonDupeFilter()
    
    def push(self,request):
        """
        解析request协议,将request投入到协议指定的调度器中
        """
        if self._dupefilter.put(request):
            #将request放到scheduler中
            return True
        else:
            return False

    

#*-*coding:utf8*-*
#  gevent 为 python-lib 打了 patch
from gevent import monkey
monkey.patch_all()

import threading
import gevent.monkey
gevent.monkey.patch_thread()
import gevent.pool as GEVP

from SimpleXMLRPCServer import SimpleXMLRPCServer
from xmlrpclib import ServerProxy


#  RPCNative / RPCProxy 将来还要再抽象，把 XML 和 Thrift 等 RPC 通信协议也抽象出来
class RPCNativeBase(object):
    def __init__(self, nativeObject, binderPort):
        self.native = nativeObject
        self.server = SimpleXMLRPCServer(('localhost', binderPort))
        self.server.register_instance(self.native)
        self.__backThread = GEVP.Pool(1)

    def __runServer(self, name):
        try:
            print "Running " + name
            self.__name = name
            self.server.serve_forever()
        except (KeyboardInterrupt):
            self.server.server_close()
            print "Receive KeyboardInterrupt in " + name
        finally:
            self.server.server_close()

    def __del__(self):
        self.stopNative()

    # startNative will be blocked and wait
    def startNative(self):
        self.__backThread.spawn(self.__runServer, self.__class__.__name__)

    def stopNative(self):
        self.server.shutdown()
        self.__backThread.join()
        self.server.server_close()
        print "Stopped " + self.__class__.__name__


class RPCProxyBase(object):

    # [remoteInfo] must be type of string to interpret remote ip:port such us "http://localhost:8080"
    def __init__(self, remoteInfo):
        self._proxy = ServerProxy(remoteInfo)

    @property
    def proxy(self):
        return self._proxy


# Client machine may need keep more than 1 rpc connections to [RPCNativeBase]
class RPCProxyManager(object):
    def __init__(self):
        # {proxyType:{proxyName:BpBinderOject, proxyName:BpBinderOject}, proxyType:{proxyName:BpBinderObject, proxyName:BpBinderObject}, ... ... }
        self.__inner_proxy_bucket = dict()

    def getProxy(self, proxyType, proxyName):
        try:
            return self.__inner_proxy_bucket[proxyType][proxyName]
        except (Exception, TypeError) as e:
            print e
            return None

    def buildRPCProxy(self,
                      remoteInfo,
                      proxyType,
                      proxyName,
                      packet_name='Araneae.rpc', ):

        _module_home = __import__(packet_name, globals(), locals(), [proxyType
                                                                     ])
        bpBinder = getattr(_module_home, proxyType)(remoteInfo, proxyName)

        if not self.__inner_proxy_bucket.has_key(proxyType):
            self.__inner_proxy_bucket[proxyType] = dict()

        self.__inner_proxy_bucket[proxyType][proxyName] = bpBinder

    def showAllKeys(self):
        all_keys = ""

        for key in self.__inner_proxy_bucket.keys():
            for key1 in self.__inner_proxy_bucket[key].keys():
                all_keys = all_keys + "{" + str(key) + "-" + str(key1) + "} "

        return all_keys

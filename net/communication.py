#*-*coding:utf8*-*

import six
import gevent
from gevent import socket
from abc import ABCMeta, abstractmethod
from gevent.server import StreamServer, DatagramServer


class TCPServer(object):

    __metaclass__ = ABCMeta

    def __init__(self, port=5000):
        self._port = port
        self._ssh = StreamServer(('localhost', port), self.transaction)

    @abstractmethod
    def transaction(self, socket, address):
        pass

    def start(self):
        self._ssh.serve_forever()


class TCPClient(object):
    def __init__(self, address, port):
        self._address = address
        self._port = port
        self._sock = socket.socket(type=socket.SOCK_STREAM)
        self._sock.connect((self._address, self._port))

    def send(self, data):
        self._sock.send(data)

    def __del__(self):
        self._sock.close()
        pass


LOST_HEART = 10
HEART_BEAT_LENGTH = 100
CLIENT_HEART_BEAT = 'Quee'
SERVER_HEART_BEAT = 'Area'


class HeartBeatServer(DatagramServer):
    def __init__(self, port):
        port = ':' + str(port)
        super(HeartBeatServer, self).__init__(port)
        self._client_counter = {}

    def handle(self, data, address):
        if data == CLIENT_HEART_BEAT:
            self._client_counter.setdefault(data, 0)
            self._beat(data, address)

    def _beat(self, data, address):
        print '%s -- %s' % (data, address)
        self.socket.sendto(SERVER_HEART_BEAT, address)

    def timer(self):
        self._client_counter = {
            client: counter + 1
            for client, counter in six.iteritems(self._client_counter)
        }

    def is_lost(self, client):
        counter = self._client_counter.get(client, False)

        if counter > LOST_HEART:
            return True
        else:
            return False

    def list_client(self):
        return self._client_counter.keys()

    def list_lost_client(self):
        return [client
                for client, counter in six.iteritems(self._client_counter)
                if self.is_lost(client)]


class HeartBeatClient(object):
    def __init__(self, address, port):
        self._address = address
        self._port = port
        self._sock = socket.socket(type=socket.SOCK_DGRAM)
        self._sock.connect((self._address, self._port))
        self._counter = 0

    def beat(self):
        self._sock.send(CLIENT_HEART_BEAT)
        confirm = self._sock.recv(HEART_BEAT_LENGTH)

        if confirm == SERVER_HEART_BEAT:
            self._counter = 0

    def timer(self):
        self._counter += 1

    def is_lost(self):
        if self._counter > LOST_HEART:
            return True
        else:
            return False

#tcp server and client

#!coding:utf8

from Araneae.compat import json as Json
from Araneae.utils.python import to_native_str
from Araneae.utils.request import request_unpickle
from Araneae.protocols.scheduler import SchedulerProtocol


def protocol_string_to_object(protocol_string):
    protocol_json = Json.loads(protocol_string)
    protocol_json['request'] = request_unpickle(to_native_str(protocol_json['request']))
    return SchedulerProtocol(**protocol_json)


if __name__ == '__main__':
    from Araneae.http.request import Request
    r = Request('www.baidu.com')
    protocol = SchedulerProtocol(r,scheduler_name = 'demo',rule_number = 1)
    p_string = protocol.to_json_string()
    print p_string

    p2 = protocol_string_to_object(p_string)
    print id(protocol) 
    print id(p2)

    print p2.request

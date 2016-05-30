#*-*coding:utf8*-*
"""
生成类函数
"""

import json
import lxml.html
import lxml.html.soupparser

from hashlib import md5
from importlib import import_module


def response2dom(response):
    #decode('utf8')转换成utf8，否则会报错
    return lxml.html.soupparser.fromstring(response.text, features='html5lib')

def load_class(class_path, *targs, **kvargs):
    try:
        dot_idx = class_path.rfind('.')
        module_path = class_path[:dot_idx]
        class_name = class_path[dot_idx + 1:]
        module = import_module(module_path)
        obj = getattr(module, class_name)(*targs, **kvargs)
    except (TypeError, ImportError):
        raise TypeError('确保类路径和参数正确')

    return obj

def printfinger_request(request):
    try:
        request = json.loads(request)
        url = request['url']
        method = request['method']
        return md5(url + method).hexdigest()
    except ValueError:
        return md5(request)



if __name__ == '__main__':
    print load_class('neae.middleware.RandomMiddleWare', 'Araneae.man.setting')

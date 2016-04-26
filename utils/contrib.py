#*-*coding:utf8*-*
"""
生成类函数
"""

import lxml.html
import lxml.html.soupparser 

from importlib import import_module


def response2dom(response):
    #try:
    #    dom = lxml.html.fromstring(response.content)
    #except UnicodeDecodeError:
    dom = lxml.html.soupparser.fromstring(response.content,features = 'html5lib')

    return dom

def load_class(class_path,*targs,**kvargs):
    try:  
        dot_idx = class_path.rfind('.')
        module_path = class_path[:dot_idx]
        class_name = class_path[dot_idx+1:]
        module = import_module(module_path)
        obj = getattr(module,class_name)(*targs,**kvargs)
    except (TypeError,ImportError):
        raise TypeError('确保类路径和参数正确')

    return obj

if __name__ == '__main__':
    print load_class('neae.middleware.RandomMiddleWare','Araneae.man.setting')

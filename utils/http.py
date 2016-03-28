#*-*coding:utf8*-*

import urlparse

def revise_url(url):
    if not urlparse.urlparse(url).scheme:
        return 'http://' + url
    else
        return url

def validate_method(method):
    method = method.lower()

    allow_method = ['get','post','put','delete','head','options']

    if method in allow_method:
        return method
    else:
        raise TypeError('http请求方法错误')

    


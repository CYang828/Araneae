#*-*coding:utf8*-*

import urlparse

def revise_url(url):
    if not urlparse.urlparse(url).scheme:
        return 'http://' + url
    else:
        return url

def replenish_url(response,url):
    """
    补全url的域名
    """
    url_info = urlparse.urlparse(url)
    response_url_info = urlparse.urlparse(response.url) 

    if not url_info.scheme and not url_info.hostname:
        return response_url_info.scheme + '://' + response_url_info.hostname + 'url'
    else:
        return url

def validate_method(method):
    method = method.lower()

    allow_method = ['get','post','put','delete','head','options']

    if method in allow_method:
        return method
    else:
        raise TypeError('http请求方法错误')


    


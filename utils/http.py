#*-*coding:utf8*-*

import urlparse
from w3lib import html


def revise_url(url):
    if not urlparse.urlparse(url).scheme:
        return 'http://' + url
    else:
        return url


def replenish_url(response, url):
    """
    补全url的域名
    """
    url_tuple = urlparse.urlparse(url)
    base_url = html.get_base_url(response.content, response.url, response.encoding)

    #网址已经是一个绝对地址,返回url
    if url_tuple.scheme and url_tuple.hostname:
        return url

    #网页没有设置base_url的情况,get_base_url返回网页地址
    if base_url == response.url:
        response_tuple = urlparse.urlparse(response.url)
        print urlparse.urljoin(response_tuple.scheme + '://' + response_tuple.hostname, url)
        return urlparse.urljoin(response_tuple.scheme + '://' + response_tuple.hostname, url)
    else:
        print urlparse.urljoin(base_url,url)
        return urlparse.urljoin(base_url,url)

def validate_method(method):
    method = method.lower()

    allow_method = ['get', 'post', 'put', 'delete', 'head', 'options']

    if method in allow_method:
        return method
    else:
        raise TypeError('http请求方法错误')

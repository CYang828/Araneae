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
    base_url = html.get_base_url(response.content, response.url, response.encoding)
    url_info = urlparse.urlparse(url)

    if not url_info.scheme and not url_info.hostname:
        if url[0] != '/':
            return base_url + url
        else:
            return base_url + url[1:]
    else:
        return url


def validate_method(method):
    method = method.lower()

    allow_method = ['get', 'post', 'put', 'delete', 'head', 'options']

    if method in allow_method:
        return method
    else:
        raise TypeError('http请求方法错误')

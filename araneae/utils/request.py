#!coding:utf8

import six
import cPickle as pickle

from Araneae.http.request import Request


def request_pickle(request):
    return pickle.dumps(request, protocol = True)

def request_unpickle(pickle_request):
    return pickle.loads(pickle_request)

def url_to_request(url, callback = None):
    if isinstance(url, six.string_types):
        return Reuquest(url,callback = callback)
    elif isinstance(url, dict):
        url['callback'] = callback
        return Request(**url)

def urls_to_requests(urls, callback = None):
    return [url_to_request(url,callback) for url in urls]

if __name__ == '__main__':
    from Araneae.http.request import Request
    r = Request('http://www.sohu.com/')
    p = request_pickle(r)
    print p

    un_p = request_unpickle(p)
    print un_p
    print un_p.url

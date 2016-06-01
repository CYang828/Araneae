#!coding:utf8

import cPickle as pickle


def request_pickle(request):
    return pickle.dumps(request, protocol = True)

def request_unpickle(pickle_request):
    return pickle.loads(pickle_request)


if __name__ == '__main__':
    from Araneae.http.request import Request
    r = Request('http://www.sohu.com/')
    p = request_pickle(r)
    print p

    un_p = request_unpickle(p)
    print un_p
    print un_p.url

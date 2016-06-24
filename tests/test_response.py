# coding:utf8

import unittest
from requests import get

from araneae.http import Response


class ResponseTestCase(unittest.TestCase):

    def setUp(self):
        url = 'http://www.baidu.com'
        self.response = Response(get(url))

    def test_selector(self):
        print self.response.selector

    def test_base_url(self):
        print self.response.get_base_url()

    def test_text(self):
        #print self.response.text()
        pass

    def test_content(self):
        #print self.response.content()
        pass

    def test_print(self):
        print self.response


if __name__ == '__main__':
    unittest.main()

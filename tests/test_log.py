# coding:utf8

import unittest

from araneae.utils.log import get_logger

class LogTestCase(unittest.TestCase):

    def setUp(self):
        self.logger1 = get_logger('logs/test.log')
        self.logger2 = get_logger('test1')
        self.logger3 = get_logger('test2')
        self.logger4 = get_logger('logs/test.log')
        self.logger5 = get_logger('test1')

    def test_debug(self):
        self.logger1.debug('debug logger1')
        self.logger2.debug('debug logger2')
        self.logger3.debug('debug logger3')
        self.logger4.debug('debug logger4')
        self.logger5.debug('debug logger5')

    def test_info(self):
        self.logger1.info('info logger1')
        self.logger2.info('info logger2')
        self.logger3.info('info logger3')
        self.logger4.info('info logger4')
        self.logger5.info('info logger5')

    def test_warn(self):
        self.logger1.warn('warn logger1')
        self.logger2.warn('warn logger2')
        self.logger3.warn('warn logger3')
        self.logger4.warn('warn logger4')
        self.logger5.warn('warn logger5')

    def test_error(self):
        self.logger1.error('error logger1')
        self.logger2.error('error logger2')
        self.logger3.error('error logger3')
        self.logger4.error('error logger4')
        self.logger5.error('error logger5')

    def test_equal(self):
        self.assertEqual(self.logger1, self.logger4)
        self.assertEqual(self.logger2, self.logger5)

    def test_chinese(self):
        s = '中文'
        self.logger2.error(s)

if __name__ == '__main__':
    unittest.main()


        




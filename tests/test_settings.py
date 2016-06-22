# coding:utf8

import unittest

from araneae.utils.settings import Settings

class SettingsTestCase(unittest.TestCase):

    def setUp(self):
        self.settings1 = Settings('Araneae.tests.settings.test_settings')

    def test_get(self):
        self.assertEqual(self.settings1.get('NON'), None)
        self.assertEqual(self.settings1.get('name'), 'test')
        self.assertEqual(self.settings1.get('NAME'), 'test')
        self.assertEqual(self.settings1.getlist('LIST'), ['log1','log2','log3'])
        self.assertEqual(self.settings1.getint('INT'), 1)
        self.assertEqual(self.settings1.getfloat('FLOAT'), 1.00)

    def test_set(self):
        self.settings1.set_from_dict({'key':'value'})
        self.assertEqual(self.settings1.get('key'), 'value')
        self.settings1.set_from_value('key1','value1')
        self.assertEqual(self.settings1.get('key1'), 'value1')

    def test_reset(self):
        self.settings1.reset()


if __name__ == '__main__':
    unittest.main()

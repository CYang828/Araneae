# coding:utf8

import unittest

from araneae.core.piker import RulePicker

class RulePickerTestCase(unittest.TestCase):

    def setUp(self):
        self.picker = RulePicker()

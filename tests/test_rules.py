# coding:utf8

import unittest
from requests import get

from araneae.rules.chain import ChainRule
from araneae.utils.settings import Settings
from araneae.utils.loader import load_object


class RulesTestCase(unittest.TestCase):

    def setUp(self):
        ext_data_setting = {'extract_data':{'type':'tree','child1':{'type':'xpath','expression':' //*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[*]/td/table/tbody/tr/td[1]/a/text()','field':'child1'},'child2':{'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[!PAR]/td/table/tbody/tr/td[2]/table/tbody/tr[*]/td[*]/a/text()','field':'child2'}}}

        self.chain = load_object('araneae.rules.chain.ChainRule').from_settings(ext_data_setting)

    def test_chain_rule(self):
        url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm'
        response = get(url)
        #数据抽取器
        print self.chain.data_extractor.extract(response)


if __name__ == '__main__':
    unittest.main()

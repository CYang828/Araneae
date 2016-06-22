# coding:utf8

import unittest
from requests import get

from araneae.extractors import DataExtractor

class ExtractorsTestCase(unittest.TestCase):

    def setUp(self):
        ext_data_setting1 = {'type':'css','expression':'div.tbkt_title > a.active > span','field':'subject'}
        self.data_extractor1 = DataExtractor(ext_data_setting1)
        ext_data_setting2 = {'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td[1]/a/text()','field':'edition'}
        self.data_extractor2 = DataExtractor(ext_data_setting2)

        ext_data_setting3 = {'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'edition'}
        self.data_extractor3 = DataExtractor(ext_data_setting3)

        ext_data_setting4 = {'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'link','mulrecord':True}
        self.data_extractor4 = DataExtractor(ext_data_setting4)

        ext_data_setting5 = [{'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'link','mulrecord':True},
                             {'type':'css','expression':'div.tbkt_title > a.active > span','field':'subject','parent':0}]
        self.data_extractor5 = DataExtractor(ext_data_setting5)

        ext_data_setting6 = [{'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'link','mulrecord':True},
                             {'type':'css','expression':'div.tbkt_title > a.active > span','field':'subject','parent':0},
                             {'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td[1]/a/text()','field':'edition','parent':1}]
        self.data_extractor6 = DataExtractor(ext_data_setting6)

        ext_data_setting7 = {'type':'tree',
                             'root':{'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody'},
                             'child1':{'type':'xpath','expression':'.//tr[*]/td/table/tbody/tr/td[1]/a','field':'child1'},
                             'child2':{'type':'xpath','expression':'.//tr[!PAR]/td/table/tbody/tr/td[2]/table/tbody/tr[*]/td[*]/a/text()','field':'child2'}}
        self.data_extractor7 = DataExtractor(ext_data_setting7)


    def test_data_extracotr(self):
        url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm'
        response = get(url)
        print response
        #css测试
        #self.data_extractor1.extract(response)
        #xpath测试
        #self.data_extractor2.extract(response)
        #re测试
        #self.data_extractor3.extract(response)
        #多条数据测试
        #self.data_extractor4.extract(response)
        #父子级数据关联测试
        #self.data_extractor5.extract(response)
        #多个父子级数据关联测试
        #self.data_extractor6.extract(response)
        #树状结构数据抽取测试
        self.data_extractor7.extract(response)



if __name__ == '__main__':
    unittest.main()

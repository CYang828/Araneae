# coding:utf8

import unittest
from requests import get

from araneae.http import Response
from araneae.extractors import (DataExtractor, LinkExtractor, LinkFilterExtractor)

class ExtractorsTestCase(unittest.TestCase):

    def test_data_extracotr(self):
        ext_data_setting1 = {'type':'css','expression':'div.tbkt_title > a.active > span','field':'subject'}
        data_extractor1 = DataExtractor(ext_data_setting1)
        ext_data_setting2 = {'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td[1]/a/text()','field':'edition'}
        data_extractor2 = DataExtractor(ext_data_setting2)

        ext_data_setting3 = {'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'edition'}
        data_extractor3 = DataExtractor(ext_data_setting3)

        ext_data_setting4 = {'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'link','mulrecord':True}
        data_extractor4 = DataExtractor(ext_data_setting4)

        ext_data_setting5 = [{'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'link','mulrecord':True},
                             {'type':'css','expression':'div.tbkt_title > a.active > span','field':'subject','parent':0}]
        data_extractor5 = DataExtractor(ext_data_setting5)

        ext_data_setting6 = [{'type':'re','expression':'/Jty/tbkt/getTbkt2_currentBitCode_\d*\.shtm','field':'link','mulrecord':True},
                             {'type':'css','expression':'div.tbkt_title > a.active > span','field':'subject','parent':0},
                             {'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[1]/td/table/tbody/tr/td[2]/table/tbody/tr[3]/td[1]/a/text()','field':'edition','parent':1}]
        data_extractor6 = DataExtractor(ext_data_setting6)

        ext_data_setting7 = {'type':'tree',
                             'child1':{'type':'xpath','expression':' //*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[*]/td/table/tbody/tr/td[1]/a/text()','field':'child1'},
                             'child2':{'type':'xpath','expression':'//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody/tr[2]/td/table/tbody/tr[!PAR]/td/table/tbody/tr/td[2]/table/tbody/tr[*]/td[*]/a/text()','field':'child2'}}
        data_extractor7 = DataExtractor(ext_data_setting7)

        #url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm'
        #response = Response(get(url))
        #css测试
        #print data_extractor1.extract(response)
        #xpath测试
        #print data_extractor2.extract(response)
        #re测试
        #print data_extractor3.extract(response)
        ##多条数据测试
        #print data_extractor4.extract(response)
        #父子级数据关联测试
        #print data_extractor5.extract(response)
        #多个父子级数据关联测试
        #print data_extractor6.extract(response)
        #树状结构数据抽取测试
        #print data_extractor7.extract(response)

    def test_link_extractor(self):
        url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm'
        response = Response(get(url))

        link_extractor1 = LinkExtractor()        
        #print link_extractor1.extract_links(response)

    def test_link_filter_extractor(self):
        url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm'
        response = Response(get(url))

        link_filter_link1 = LinkFilterExtractor(allow=('/Jty/tbkt/getTbkt2_currentBitCode_001001001004.shtm'))
        print link_filter_link1.extract_links(response)


if __name__ == '__main__':
    unittest.main()

# coding:utf8

from requests import get
from parsel import Selector
from lxml.html import soupparser


url = 'http://czy.jtyhjy.com/Jty/tbkt/getTbkt_currentBitCode_001001.shtm'
response = get(url)

root = soupparser.fromstring(response.text, features='html5lib')
sel = Selector(root = root)
node1 = sel.xpath('//*[@id="mainContent"]/form/table[2]/tbody/tr/td/table/tbody')
print node1

node2 = node1.xpath('.//tr[*]/td/table/tbody/tr/td[1]/a').extract()
print node2
for node in node2:
    print node.encode('utf8')



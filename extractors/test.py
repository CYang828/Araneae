# coding:utf8

from requests import get
from parsel import Selector
from lxml.html import soupparser


url = 'http://www.jtyhjy.com/zyw/synclass/home#1'
response = get(url)

root = soupparser.fromstring(response.text, features='html5lib')
sel = Selector(root = root)
node1 = sel.xpath('//*[@id="m-bottom"]/div/div[1]')

node2 = node1.xpath('.//div[*]/@')

for n in node2:
    print n.extract()
    print '----------------------'

#这种nest的调用其实是html的内容嵌套关系
#x = lambda x: x*2

#a = {x:'1'}

#print a

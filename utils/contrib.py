#*-*coding:utf8*-*
"""
生成类函数
"""

import lxml.html
import lxml.html.soupparser 

def response2dom(response):
    #try:
    #    dom = lxml.html.fromstring(response.content)
    #except UnicodeDecodeError:
    dom = lxml.html.soupparser.fromstring(response.content,features = 'html5lib')

    return dom

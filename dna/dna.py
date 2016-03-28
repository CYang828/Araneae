#*-*coding:utf8*-*

import spider
import chromesome

from Araneae.utils.setting import Setting

SPIDER_TYPE = { 
                'RuleLink'      :   (   'RuleLinkChromesome'        ,   'RuleLinkSpider'        ),
                'BroadPriority' :   (   'BroadPriorityChromesome'   ,   'BroadPrioritySpider'   ),
                'DeepPriority'  :   (   'DeepPriorityChromesome'    ,   'DeepPrioritySpider'    ),
              }

class DNA(Setting):

    __spider_obj = None

    def generator(self):
        if self['SPIDER_TYPE']:
            chromesome_obj = getattr(chromesome,SPIDER_TYPE[self['SPIDER_TYPE']][0])(self)
            spider_obj = getattr(spider,SPIDER_TYPE[self['SPIDER_TYPE']][1])(chromesome_obj)
        else:
            raise SpiderChromesomeException('没有指定spider类型')

        self.__spider_obj = spider_obj
        #应该生成一个spider对象
        return spider_obj

if __name__ == '__main__':                                                                                                                                      
    c = DNA('spiders.demo')
    spider = c.generator()

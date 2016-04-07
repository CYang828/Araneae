#*-*coding:utf8*-*

import Araneae.dna.spider as SPD
import Araneae.utils.setting as SET
import Araneae.dna.chromesome as CHM

SPIDER_TYPE = { 
                'RuleLink'      :   (   'RuleLinkChromesome'        ,   'RuleLinkSpider'        ),
                'BroadPriority' :   (   'BroadPriorityChromesome'   ,   'BroadPrioritySpider'   ),
                'DeepPriority'  :   (   'DeepPriorityChromesome'    ,   'DeepPrioritySpider'    ),
              }

class DNA(SET.Setting):

    __spider_obj = None

    def generator(self):
        if self['SPIDER_TYPE']:
            chromesome_obj = getattr(CHM,SPIDER_TYPE[self['SPIDER_TYPE']][0])(self)
            spider_obj = getattr(SPD,SPIDER_TYPE[self['SPIDER_TYPE']][1])(chromesome_obj)
        else:
            raise SpiderChromesomeException('没有指定spider类型')

        self.__spider_obj = spider_obj
        #应该生成一个spider对象
        return spider_obj

if __name__ == '__main__':                                                                                                                                      
    import sys
    sys.path.append('/home/zhangchunyang/')
    del sys

    c = DNA('Araneae.man.default_setting')
    spider = c.generator()
    spider.start()
    spider.end()

#*-*coding:utf8*-*

import Araneae.dna.spider as SPD
import Araneae.utils.setting as SET
import Araneae.man.exception as EXP
import Araneae.dna.chromesome as CHM

SPIDER_TYPE = {
    'RuleLink': ('RuleLinkChromesome', 'RuleLinkSpider'),
    'BreadthFirst': ('BreadthFirstChromesome', 'BreadthFirstSpider'),
    'DeepPriority': ('DeepPriorityChromesome', 'DeepPrioritySpider'),
}

SPIDER_TYPE_RULELINK = 'RuleLink'
SPIDER_TYPE_BREADTHFIRST = 'BreadthFirst'

DEFAULT_SETTING = 'Araneae.man.default_setting'


class DNA(SET.Setting):

    SPIDER_TYPE_OPTIONS = {'rulelink': SPIDER_TYPE_RULELINK, 'breadthfirst': SPIDER_TYPE_BREADTHFIRST}

    __spider_objs = {}

    def __init__(self, module):
        super(DNA, self).__init__('Araneae.man.default_setting')
        super(DNA, self).__init__(module)

        self.set_options('SPIDER_TYPE', *self.SPIDER_TYPE_OPTIONS.keys())

    def generator(self):
        spider_type = self.SPIDER_TYPE_OPTIONS[self.get('SPIDER_TYPE')]

        if spider_type:
            chromesome_obj = getattr(CHM, SPIDER_TYPE[spider_type][0])(self)
            spider_obj = getattr(SPD, SPIDER_TYPE[spider_type][1])(chromesome_obj)
        else:
            raise EXP.DNAException('没有指定spider类型')

        self.__spider_objs[spider_obj.name] = spider_obj
        return spider_obj


if __name__ == '__main__':
    from gevent import monkey
    monkey.patch_all()

    c = DNA('Araneae.man.jintaiyang_setting')
    #c = DNA('Araneae.man.jintaiyang_gaozhong_setting')
    spider = c.generator()
    spider.start()
    spider.end()

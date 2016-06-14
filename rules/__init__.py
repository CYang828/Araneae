# coding:utf8

import re
from collections import OrderedDict

from Araneae.constant import PAGE_RULE_PREFIX


class SpiderRule(object):

    def _page_rule_prefix_len(self):
        return len(PAGE_RULE_PREFIX)

    def find_page_rule(self, settings):
        return {key:value for key,value in settings.iterater() if key.startswith(PAGE_RULE_PREFIX)}

    def sort_page_rule(self, settings):
        return OrderedDict(sorted(self.find_page_rule(settings).items(),key=lambda x:int(x[0][self._page_rule_prefix_len():])))
        

if __name__ == '__main__':
    from Araneae.utils.settings import Settings
    s = Settings('Araneae.man.setting')
    r = Rule()
    print r.sort_page_rule(s)
     

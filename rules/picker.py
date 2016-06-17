
import re
from collections import OrderedDict

from Araneae.utils.loader import load_object
from Araneae.constant import RULE_PREFIX


class RulePicker(object):

    def __init__(self, settings, rule_path):
        self._settings = settings
        self._rule_path = rule_path
        self.set_rules()

    def _rule_prefix_len(self):
        return len(RULE_PREFIX)

    def set_rules(self):
        rules = {key:load_object(self._rule_path).from_settings(value) for key,value in self._settings.iterater() if key.startswith(RULE_PREFIX)}
        self._rules = OrderedDict(sorted(rules.items(),key=lambda x:int(x[0][self._rule_prefix_len():])))
        self._rule_names = self._rules.keys()
        self._rule_length = len(self._rules)

    def get_next_rule(self,rule_name):
        rule_idx = self._rule_names.index(rule_name)
        return rule_idx<self._rule_length and (self._rule_names[rule_idx+1],self._rules[self._rule_names[rule_idx+1]])

    def get_previous_rule(self,rule_name):
        rule_idx = self._rule_names.index(rule_name)
        return rule_idx>0 and (self._rule_names[rule_idx-1],self._rules[self._rule_names[rule_idx-1]])

    def get_first_rule(self):
        return next(self._rules.iteritems())

class Rule(object):
        
        def __init__(self,settings):
            pass

        @classmethod 
        def from_settings(cls,settings):
            return cls(settings)

if __name__ == '__main__':
    from Araneae.utils.settings import Settings
    
    s = Settings('Araneae.man.setting')
    r = RulePicker(s)
    first_rule = r.get_first_rule()
    print first_rule
    sec = r.get_next_rule(first_rule[0])
    print r.get_next_rule(sec[0])
    

# coding:utf8 


"""
常量
"""
import re


#调度器默认拉取超时时间
DEFAULT_SCHEDULER_PULL_TIMEOUT = 5
#调度器默认拉取条数
DEFAULT_SCHEDULER_PULL_COUNT = 1

#配置文件中规则前缀
RULE_PREFIX = 'PAGE'

#树状结构数据子节点配置文件中规则前缀
TREE_DATA_CHILD_PREFIX = 'CHILD'

#树状结构数据匹配上级正则
TREE_DATA_PARENT_REGEX = re.compile(r'!PAR')


#默认request方法
DEFAULT_REQUEST_METHOD = 'GET'

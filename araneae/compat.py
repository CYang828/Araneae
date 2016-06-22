#!coding:utf8

import six
import sys

from araneae.utils.log import get_logger

logger = get_logger(__name__)

try:
    import simplejson as json
except (ImportError,SyntaxError):
    #python3.2 不支持simplejson
    import json

try:
    from collections import ChainMap
except:
    from chainmap import ChainMap
else:
    logger.error('Please install package chainmap,`pip install chainmap`')

# coding:utf8

from Araneae.spiders import Spider


class ChainSpider(Spider):
    rule_path = 'Araneae.rules.chain.ChainRule'

    def parse(self, protocol, response):
        pass


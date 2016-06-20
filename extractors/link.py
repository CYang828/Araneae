# coding:utf8

import weakref

from Araneae.utils.url import rel_has_nofollow
from Araneae.utils.extractor import response_to_selector
from Araneae.utils.python import (to_native_str,arg_to_iter)


XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"
_collect_string_content = etree.XPath("string()")

def _nons(tag):
    """移除xhtml中的namespace,获取干净的tag"""
    if isinstance(tag, six.string_types):
        if tag[0] == '{' and tag[1:len(XHTML_NAMESPACE)+1] == XHTML_NAMESPACE:
            return tag.split('}')[-1]

    return tag

class LinkExtractor(object):
    """link提取器"""

    def __init__(self, tag='a', attr='href', process=None, unique=False):
        self.scan_tag = tag if callable(tag) else lambda t: t == tag
        self.scran_attr = attr if callable(attr) else lambda a: a == attr
        self.process_attr = process if callable(process) else lambda v: v
        self.unique = unique

    def _iter_links(self, document):
        """迭代需要的tag和attr的el"""
        for el in document.iter(etree.Element):
            if not self.scan_tag(_nons(el.tag)):
                continue

            attribs = el.attrib

            for attrib in attribs:
                if not self.scan_attr(attrib):
                    continue
                yield (el, attrib, attribs[attrib])

    def _extract_links(self, selector, response_url, response_encoding, base_url):
        links = []

        # hacky way to get the underlying lxml parsed document
        for el, attr, attr_val in self._iter_links(selector.root):
            # pseudo lxml.html.HtmlElement.make_links_absolute(base_url)
            try:
                attr_val = urljoin(base_url, attr_val)
            except ValueError:
                continue # skipping bogus links
            else:
                url = self.process_attr(attr_val)

                if url is None:
                    continue

            url = to_native_str(url, encoding=response_encoding)
            # to fix relative links after process_value
            url = urljoin(response_url, url)
            link = Link(url, _collect_string_content(el) or u'', nofollow=rel_has_nofollow(el.get('rel')))
            links.append(link)

        return self._deduplicate_if_needed(links)

    def extract_links(self, response):
        selector = response_to_selector(response)   
        base_url = response.get_base_url()
        return self._extract_links(selector, response.url, response.encoding, base_url)

    def _process_links(self, links):
        """ Normalize and filter extracted links
        The subclass should override it if neccessary"""

        return self._deduplicate_if_needed(links)

    def _deduplicate_if_needed(self, links):
        if self.unique:
            return unique_list(links, key=lambda link: link.url)

        return links


"""Helper classes for tests."""

import unittest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import SoupStrainer
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder

class SoupTest(unittest.TestCase):

    default_builder = None

    def assertSoupEquals(self, to_parse, compare_parsed_to=None):
        builder = self.default_builder
        if builder is None:
            builder = LXMLTreeBuilder()
        obj = BeautifulSoup(to_parse, builder=builder)
        if compare_parsed_to is None:
            compare_parsed_to = to_parse

        self.assertEquals(
            obj.decode(),
            builder.test_fragment_to_document(compare_parsed_to))


"""Helper classes for tests."""

import unittest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import SoupStrainer

class SoupTest(unittest.TestCase):

    default_builder = None

    def assertSoupEquals(self, to_parse, compare_parsed_to=None):
        obj = BeautifulSoup(to_parse, builder=self.default_builder)
        if compare_parsed_to is None:
            compare_parsed_to = to_parse

        self.assertEquals(obj.decode(), compare_parsed_to)


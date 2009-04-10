"""Tree builder compatibility suite.

If you create a tree builder class, also create a test suite that
subclasses this one. This test suite will parse various bits of
well-formed HTML with your tree builder. Not every tree builder will
handle bad HTML in the same way, but every builder should be able to
handle _good_ HTML in the same way.
"""

import unittest
from beautifulsoup import BeautifulSoup
from test_soup import SoupTest

class CompatibilityTest(SoupTest):

    def __init__(self, builder):
        self.builder = builder

    _testMethodName = "test"

    def test(self):
        self.test_bare_string()
        self.test_tag_nesting()

    def test_bare_string(self):
        self.assertSoupEquals("A bare string")

    def test_tag_nesting(self):
        self.assertSoupEquals("<b>Inside a B tag</b>")
        self.assertSoupEquals("<p>A <i>nested <b>tag</b></i></p>")

from helpers import SoupTest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import SoupStrainer
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder
import unittest

class TestLXMLBuilder(SoupTest):

    def runTest(self):
        self.test_bare_string()
        self.test_tag_nesting()
        self.test_self_closing()
        self.test_soupstrainer()

    def test_bare_string(self):
        self.assertSoupEquals(
            "A bare string", "<p>A bare string</p>")

    def test_tag_nesting(self):
        b_tag = "<b>Inside a B tag</b>"
        self.assertSoupEquals(b_tag)

        nested_b_tag = "<p>A <i>nested <b>tag</b></i></p>"
        self.assertSoupEquals(nested_b_tag)

    def test_self_closing(self):
        self.assertSoupEquals(
            "<p>A <meta> tag</p>", "<p>A <meta /> tag</p>")

    def test_soupstrainer(self):
        strainer = SoupStrainer("b")
        soup = BeautifulSoup("A <b>bold</b> <i>statement</i>",
                             self.default_builder,
                             parseOnlyThese=strainer)
        self.assertEquals(soup.decode(), "<b>bold</b>")

        soup = BeautifulSoup("A <b>bold</b> <meta> <i>statement</i>",
                             self.default_builder,
                             parseOnlyThese=strainer)
        self.assertEquals(soup.decode(), "<b>bold</b>")


def test_suite():
    return unittest.TestLoader().loadTestsFromName('__name__')

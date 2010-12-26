from helpers import SoupTest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import SoupStrainer
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder
import unittest

class TestLXMLBuilder(SoupTest):

    def __init__(self, builder):
        super(TestLXMLBuilder, self).__init__()
        self.default_builder = LXMLTreeBuilder()

    def runTest(self):
        self.test_bare_string()
        self.test_tag_nesting()
        self.test_self_closing()
        self.test_soupstrainer()

    def document_for(self, s):
        """Turn a fragment into an HTML document.

        lxml does this to HTML fragments it receives, so we need to do it
        if we're going to understand what comes out of lxml.
        """
        return u'<html><body>%s</body></html>' % s

    def test_bare_string(self):
        self.assertSoupEquals(
            "A bare string", self.document_for("<p>A bare string</p>"))

    def test_tag_nesting(self):
        b_tag = "<b>Inside a B tag</b>"
        self.assertSoupEquals(b_tag, self.document_for(b_tag))

        nested_b_tag = "<p>A <i>nested <b>tag</b></i></p>"
        self.assertSoupEquals(nested_b_tag, self.document_for(nested_b_tag))

    def test_self_closing(self):
        self.assertSoupEquals(
            "<p>A <meta> tag</p>", self.document_for("<p>A <meta /> tag</p>"))

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

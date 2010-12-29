from helpers import SoupTest
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder


class TestLXMLBuilder(SoupTest):

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

from helpers import SoupTest
from beautifulsoup.builder.html5lib_builder import HTML5TreeBuilder


class TestHTML5Builder(SoupTest):

    def setUp(self):
        self.default_builder = HTML5TreeBuilder()

    def test_bare_string(self):
        self.assertSoupEquals("A bare string")

    def test_tag_nesting(self):
        b_tag = "<b>Inside a B tag</b>"
        self.assertSoupEquals(b_tag)

        nested_b_tag = "<p>A <i>nested <b>tag</b></i></p>"
        self.assertSoupEquals(nested_b_tag)

    def test_self_closing(self):
        self.assertSoupEquals(
            "<p>A <meta> tag</p>", "<p>A <meta /> tag</p>")


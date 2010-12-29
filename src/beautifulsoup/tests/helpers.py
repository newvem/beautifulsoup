"""Helper classes for tests."""

import unittest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import SoupStrainer
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder

class SoupTest(unittest.TestCase):

    def setUp(self):
        # LXMLTreeBuilder won't handle bad markup, but that's fine,
        # since all the parsing tests take place in parser-specific
        # test suites that override default_builder.
        self.default_builder = LXMLTreeBuilder()

    def soup(self, markup):
        """Build a Beautiful Soup object from markup."""
        return BeautifulSoup(markup, builder=self.default_builder)

    def assertSoupEquals(self, to_parse, compare_parsed_to=None):
        builder = self.default_builder
        obj = BeautifulSoup(to_parse, builder=builder)
        if compare_parsed_to is None:
            compare_parsed_to = to_parse

        self.assertEquals(
            obj.decode(),
            builder.test_fragment_to_document(compare_parsed_to))



class BuilderSmokeTest(SoupTest):
    """A generic smoke test for tree builders.

    Subclasses of this test ensure that all of Beautiful Soup's tree
    builders generate more or less the same trees. It's okay for trees
    to differ, especially when given invalid markup--just override the
    appropriate test method to demonstrate how one tree builder
    differs from others.
    """

    def test_bare_string(self):
        # A bare string is turned into some kind of HTML document or
        # fragment recognizable as the original string.
        self.assertSoupEquals("A bare string")

    def test_self_closing(self):
        # HTML's self-closing tags are recognized as such.
        self.assertSoupEquals(
            "<p>A <meta> tag</p>", "<p>A <meta /> tag</p>")

    def test_nested_inline_elements(self):
        # Inline tags can be nested indefinitely.
        b_tag = "<b>Inside a B tag</b>"
        self.assertSoupEquals(b_tag)

        nested_b_tag = "<p>A <i>nested <b>tag</b></i></p>"
        self.assertSoupEquals(nested_b_tag)

        double_nested_b_tag = "<p>A <a>doubly <i>nested <b>tag</b></i></a></p>"
        self.assertSoupEquals(nested_b_tag)

    def test_nested_block_level_elements(self):
        soup = self.soup('<blockquote><p><b>Foo</b></p></blockquote>')
        blockquote = soup.blockquote
        self.assertEqual(blockquote.p.b.string, 'Foo')
        self.assertEqual(blockquote.b.string, 'Foo')


class BuilderInvalidMarkupSmokeTest(SoupTest):
    """Tests of invalid markup.

    These are very likely to give different results for different tree
    builders.

    It's not required that a tree builder handle invalid markup at
    all.
    """

    def test_unclosed_block_level_elements(self):
        # Unclosed block-level elements should be closed.
        self.assertSoupEquals(
            '<blockquote><p><b>Foo</blockquote><p>Bar',
            '<blockquote><p><b>Foo</b></p></blockquote><p>Bar</p>')

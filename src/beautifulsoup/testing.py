"""Helper classes for tests."""

import unittest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import Comment, SoupStrainer
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder

class SoupTest(unittest.TestCase):

    def setUp(self):
        # LXMLTreeBuilder won't handle bad markup, but that's fine,
        # since all the parsing tests take place in parser-specific
        # test suites that override default_builder.
        self.default_builder = LXMLTreeBuilder()

    def soup(self, markup, **kwargs):
        """Build a Beautiful Soup object from markup."""
        return BeautifulSoup(markup, builder=self.default_builder, **kwargs)

    def document_for(self, markup):
        """Turn an HTML fragment into a document.

        The details depend on the builder.
        """
        return self.default_builder.test_fragment_to_document(markup)

    def assertSoupEquals(self, to_parse, compare_parsed_to=None):
        builder = self.default_builder
        obj = BeautifulSoup(to_parse, builder=builder)
        if compare_parsed_to is None:
            compare_parsed_to = to_parse

        self.assertEquals(obj.decode(), self.document_for(compare_parsed_to))



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

    def test_mixed_case_tags(self):
        # Mixed-case tags are folded to lowercase.
        self.assertSoupEquals(
            "<a><B><Cd><EFG></efg></CD></b></A>",
            "<a><b><cd><efg></efg></cd></b></a>")

    def test_self_closing(self):
        # HTML's self-closing tags are recognized as such.
        self.assertSoupEquals(
            "<p>A <meta> tag</p>", "<p>A <meta /> tag</p>")

        self.assertSoupEquals(
            "<p>Foo<br/>bar</p>", "<p>Foo<br />bar</p>")

    def test_comment(self):
        # Comments are represented as Comment objects.
        markup = "<p>foo<!--foobar-->baz</p>"
        self.assertSoupEquals(markup)

        soup = self.soup(markup)
        comment = soup.find(text="foobar")
        self.assertEquals(comment.__class__, Comment)

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

    def test_collapsed_whitespace(self):
        """In most tags, whitespace is collapsed."""
        self.assertSoupEquals("<p>   </p>", "<p> </p>")

    def test_preserved_whitespace_in_pre_and_textarea(self):
        """In <pre> and <textarea> tags, whitespace is preserved."""
        self.assertSoupEquals("<pre>   </pre>")
        self.assertSoupEquals("<textarea> woo  </textarea>")

    def test_single_quote_attribute_values_become_double_quotes(self):
        self.assertSoupEquals("<foo attr='bar'></foo>",
                              '<foo attr="bar"></foo>')

    def test_attribute_values_with_nested_quotes_are_left_alone(self):
        text = """<foo attr='bar "brawls" happen'>a</foo>"""
        self.assertSoupEquals(text)

    def test_attribute_values_with_double_nested_quotes_get_quoted(self):
        text = """<foo attr='bar "brawls" happen'>a</foo>"""
        soup = self.soup(text)
        soup.foo['attr'] = 'Brawls happen at "Bob\'s Bar"'
        self.assertSoupEquals(
            soup.foo.decode(),
            """<foo attr='Brawls happen at "Bob&squot;s Bar"'>a</foo>""")

    def test_ampersand_in_attribute_value_gets_quoted(self):
        self.assertSoupEquals('<this is="really messed up & stuff"></this>',
                              '<this is="really messed up &amp; stuff"></this>')


class BuilderInvalidMarkupSmokeTest(SoupTest):
    """Tests of invalid markup.

    These are very likely to give different results for different tree
    builders. It's not required that a tree builder handle invalid
    markup at all.
    """

    def test_unclosed_block_level_elements(self):
        # Unclosed block-level elements should be closed.
        self.assertSoupEquals(
            '<blockquote><p><b>Foo</blockquote><p>Bar',
            '<blockquote><p><b>Foo</b></p></blockquote><p>Bar</p>')

    def test_fake_self_closing_tag(self):
        # If a self-closing tag presents as a normal tag, the 'open'
        # tag is treated as an instance of the self-closing tag and
        # the 'close' tag is ignored.
        self.assertSoupEquals(
            "<item><link>http://foo.com/</link></item>",
            "<item><link />http://foo.com/</item>")

    def test_boolean_attribute_with_no_value_gets_empty_value(self):
        soup = self.soup("<table><td nowrap>foo</td></table>")
        self.assertEquals(soup.table.td['nowrap'], '')

    def test_incorrectly_nested_tables(self):
        self.assertSoupEquals(
            '<table><tr><table><tr id="nested">',
            '<table><tr><table><tr id="nested"></tr></table></tr></table>')




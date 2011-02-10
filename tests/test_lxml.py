"""Tests to ensure that the lxml tree builder generates good trees."""

import re

from beautifulsoup import BeautifulSoup
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder
from beautifulsoup.element import Comment
from beautifulsoup.testing import SoupTest


class TestLXMLBuilder(SoupTest):
    """A smoke test for the LXML tree builders.

    Subclass this to test some other tree builder. Subclasses of this
    test ensure that all of Beautiful Soup's tree builders generate
    more or less the same trees. It's okay for trees to differ,
    especially when given invalid markup--just override the
    appropriate test method to demonstrate how one tree builder
    differs from the LXML builder.
    """

    def test_bare_string(self):
        # A bare string is turned into some kind of HTML document or
        # fragment recognizable as the original string.
        #
        # In this case, lxml puts a <p> tag around the bare string.
        self.assertSoupEquals(
            "A bare string", "<p>A bare string</p>")

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

    # This is a <table> tag containing another <table> tag in one of its
    # cells.
    TABLE_MARKUP_1 = ('<table id="1">'
                     '<tr>'
                     "<td>Here's another table:"
                     '<table id="2">'
                     '<tr><td>foo</td></tr>'
                     '</table></td>')

    def test_correctly_nested_tables(self):
        markup = ('<table id="1">'
                  '<tr>'
                  "<td>Here's another table:"
                  '<table id="2">'
                  '<tr><td>foo</td></tr>'
                  '</table></td>')

        self.assertSoupEquals(
            markup,
            '<table id="1"><tr><td>Here\'s another table:'
            '<table id="2"><tr><td>foo</td></tr></table>'
            '</td></tr></table>')

        self.assertSoupEquals(
            "<table><thead><tr><td>Foo</td></tr></thead>"
            "<tbody><tr><td>Bar</td></tr></tbody>"
            "<tfoot><tr><td>Baz</td></tr></tfoot></table>")

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

    def test_literal_in_textarea(self):
        # Anything inside a <textarea> is supposed to be treated as
        # the literal value of the field, (XXX citation needed).
        #
        # But, both lxml and html5lib do their best to parse the
        # contents of a <textarea> as HTML.
        text = '<textarea>Junk like <b> tags and <&<&amp;</textarea>'
        soup = BeautifulSoup(text)
        self.assertEquals(len(soup.textarea.contents), 2)
        self.assertEquals(soup.textarea.contents[0], u"Junk like ")
        self.assertEquals(soup.textarea.contents[1].name, 'b')
        self.assertEquals(soup.textarea.b.string, u" tags and ")

    def test_literal_in_script(self):
        # The contents of a <script> tag are treated as a literal string,
        # even if that string contains HTML.
        javascript = 'if (i < 2) { alert("<b>foo</b>"); }'
        soup = BeautifulSoup('<script>%s</script>' % javascript)
        self.assertEquals(soup.script.string, javascript)

    def test_naked_ampersands(self):
        # Ampersands are left alone.
        text = "<p>AT&T</p>"
        soup = self.soup(text)
        self.assertEquals(soup.p.string, "AT&T")

        # Even if they're in attribute values.
        invalid_url = '<a href="http://example.org?a=1&b=2;3">foo</a>'
        soup = self.soup(invalid_url)
        self.assertEquals(soup.a['href'], "http://example.org?a=1&b=2;3")

    def test_entities_in_strings_converted_during_parsing(self):
        # Both XML and HTML entities are converted to Unicode characters
        # during parsing.
        text = "<p>&lt;&lt;sacr&eacute;&#32;bleu!&gt;&gt;</p>"
        expected = u"<p><<sacr\N{LATIN SMALL LETTER E WITH ACUTE} bleu!>></p>"
        self.assertSoupEquals(text, expected)

    def test_entities_in_attribute_values_converted_during_parsing(self):
        text = '<x t="pi&#241ata">'
        expected = u"pi\N{LATIN SMALL LETTER N WITH TILDE}ata"
        soup = self.soup(text)
        self.assertEquals(soup.x['t'], expected)

        text = '<x t="pi&#xf1;ata">'
        soup = self.soup(text)
        self.assertEquals(soup.x['t'], expected)

        text = '<x t="sacr&eacute; bleu">'
        soup = self.soup(text)
        self.assertEquals(
            soup.x['t'],
            u"sacr\N{LATIN SMALL LETTER E WITH ACUTE} bleu")

        # This can cause valid HTML to become invalid.
        valid_url = '<a href="http://example.org?a=1&amp;b=2;3">foo</a>'
        soup = self.soup(valid_url)
        self.assertEquals(soup.a['href'], "http://example.org?a=1&b=2;3")

    def test_smart_quotes_converted_on_the_way_in(self):
        # Microsoft smart quotes are converted to Unicode characters during
        # parsing.
        quote = "<p>\x91Foo\x92</p>"
        soup = self.soup(quote)
        self.assertEquals(
            soup.p.string,
            u"\N{LEFT SINGLE QUOTATION MARK}Foo\N{RIGHT SINGLE QUOTATION MARK}")

    def test_non_breaking_spaces_converted_on_the_way_in(self):
        soup = self.soup("<a>&nbsp;&nbsp;</a>")
        self.assertEquals(soup.a.string, u"\N{NO-BREAK SPACE}" * 2)

    # Tests below this line need work.

    #def test_doctype(self):
    #    xml = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"><html>foo</html></p>'
    #    self.assertSoupEquals(xml)


    #def test_cdata(self):
    #    print self.soup("<div><![CDATA[foo]]></div>")

    def test_entities_converted_on_the_way_out(self):
        text = "<p>&lt;&lt;sacr&eacute;&#32;bleu!&gt;&gt;</p>"
        expected = u"&lt;&lt;sacr\N{LATIN SMALL LETTER E WITH ACUTE} bleu!&gt;&gt;".encode("utf-8")
        soup = BeautifulSoup(text)
        str = soup.p.string
        #self.assertEquals(str.encode("utf-8"), expected)

    def test_foo(self):
        isolatin = """<html><meta http-equiv="Content-type" content="text/html; charset=ISO-Latin-1" />Sacr\xe9 bleu!</html>"""
        soup = self.soup(isolatin)

        utf8 = isolatin.replace("ISO-Latin-1".encode(), "utf-8".encode())
        utf8 = utf8.replace("\xe9", "\xc3\xa9")
        #print soup


class TestLXMLBuilderInvalidMarkup(SoupTest):
    """Tests of invalid markup for the LXML tree builder.

    Subclass this to test other builders.

    These are very likely to give different results for different tree
    builders. It's not required that a tree builder handle invalid
    markup at all.
    """

    def test_table_containing_bare_markup(self):
        # Markup should be in table cells, not directly in the table.
        self.assertSoupEquals("<table><div>Foo</div></table>")

    def test_incorrectly_nested_table(self):
        # The second <table> tag is floating in the <tr> tag
        # rather than being inside a <td>.
        bad_markup = ('<table id="1">'
                      '<tr>'
                      "<td>Here's another table:</td>"
                      '<table id="2">'
                      '<tr><td>foo</td></tr>'
                      '</table></td>')

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

    def test_doctype_in_body(self):
        markup = "<p>one<!DOCTYPE foobar>two</p>"
        self.assertSoupEquals(markup)


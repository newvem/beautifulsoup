"""Tests to ensure that the lxml tree builder generates good trees."""

import re

from beautifulsoup import BeautifulSoup
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder
from beautifulsoup.element import Comment, Doctype
from beautifulsoup.testing import SoupTest


class TestLXMLBuilder(SoupTest):
    """A smoke test for the LXML tree builders.

    Subclass this to test some other tree builder. Subclasses of this
    test ensure that all of Beautiful Soup's tree builders generate
    more or less the same trees. It's okay for trees to differ--just
    override the appropriate test method to demonstrate how one tree
    builder differs from the LXML builder. But in general, all tree
    builders should generate trees that make most of these tests pass.
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

    def test_cdata_where_its_ok(self):
        # lxml strips CDATA sections, no matter where they occur.
        markup = "<svg><![CDATA[foobar]]>"
        self.assertSoupEquals(markup, "<svg></svg>")

    def _test_doctype(self, doctype_fragment):
        """Run a battery of assertions on a given doctype string."""
        doctype_str = '<!DOCTYPE %s>' % doctype_fragment
        markup = doctype_str + '<p>foo</p>'
        soup = self.soup(markup)
        doctype = soup.contents[0]
        self.assertEquals(doctype.__class__, Doctype)
        self.assertEquals(doctype, doctype_fragment)
        self.assertEquals(str(soup)[:len(doctype_str)], doctype_str)

        # Make sure that the doctype was correctly associated with the
        # parse tree and that the rest of the document parsed.
        self.assertEquals(soup.p.contents[0], 'foo')

    def test_doctype(self):
        # Test a normal HTML doctype you'll commonly see in a real document.
        self._test_doctype(
            'html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"')

    def test_namespaced_system_doctype(self):
        # Test a namespaced doctype with a system id.
        self._test_doctype('xsl:stylesheet SYSTEM "htmlent.dtd"')

    def test_namespaced_system_doctype(self):
        # Test a namespaced doctype with a public id.
        self._test_doctype('xsl:stylesheet PUBLIC "htmlent.dtd"')

    def test_real_iso_latin_document(self):
        # Smoke test of interrelated functionality, using an
        # easy-to-understand document.

        # Here it is in Unicode. Note that it claims to be in ISO-Latin-1.
        unicode_html = u'<html><head><meta content="text/html; charset=ISO-Latin-1" http-equiv="Content-type" /></head><body><p>Sacr\N{LATIN SMALL LETTER E WITH ACUTE} bleu!</p></body></html>'

        # That's because we're going to encode it into ISO-Latin-1, and use
        # that to test.
        iso_latin_html = unicode_html.encode("iso-8859-1")

        # Parse the ISO-Latin-1 HTML.
        soup = self.soup(iso_latin_html)
        # Encode it to UTF-8.
        result = soup.encode("utf-8")

        # What do we expect the result to look like? Well, it would
        # look like unicode_html, except that the META tag would say
        # UTF-8 instead of ISO-Latin-1.
        expected = unicode_html.replace("ISO-Latin-1", "utf-8")

        # And, of course, it would be in UTF-8, not Unicode.
        expected = expected.encode("utf-8")

        # Ta-da!
        self.assertEquals(result, expected)

    def test_real_shift_jis_document(self):
        # Smoke test to make sure the parser can handle a document in
        # Shift-JIS encoding, without choking.
        shift_jis_html = (
            '<html><head></head><body><pre>'
            '\x82\xb1\x82\xea\x82\xcdShift-JIS\x82\xc5\x83R\x81[\x83f'
            '\x83B\x83\x93\x83O\x82\xb3\x82\xea\x82\xbd\x93\xfa\x96{\x8c'
            '\xea\x82\xcc\x83t\x83@\x83C\x83\x8b\x82\xc5\x82\xb7\x81B'
            '</pre></body></html>')
        unicode_html = shift_jis_html.decode("shift-jis")
        soup = self.soup(shift_jis_html)

        # Make sure the parse tree is correctly encoded to various
        # encodings.
        self.assertEquals(soup.encode("utf-8"), unicode_html.encode("utf-8"))
        self.assertEquals(soup.encode("euc_jp"), unicode_html.encode("euc_jp"))

    # Tests below this line need work.

    def test_meta_tag_reflects_current_encoding(self):
        # Here's the <meta> tag saying that a document is
        # encoded in Shift-JIS.
        meta_tag = ('<meta content="text/html; charset=x-sjis" '
                    'http-equiv="Content-type" />')

        # Here's a document incorporating that meta tag.
        shift_jis_html = (
            '<html><head>\n%s\n'
            '<meta http-equiv="Content-language" content="ja" />'
            '</head><body>Shift-JIS markup goes here.') % meta_tag
        soup = self.soup(shift_jis_html)

        # Parse the document, and the charset is replaced with a
        # generic value.
        parsed_meta = soup.find('meta', {'http-equiv': 'Content-type'})
        self.assertEquals(parsed_meta['content'],
                          'text/html; charset=%SOUP-ENCODING%')
        self.assertEquals(parsed_meta.contains_substitutions, True)

        # For the rest of the story, see TestSubstitutions in
        # test_tree.py.

    def test_entities_converted_on_the_way_out(self):
        text = "<p>&lt;&lt;sacr&eacute;&#32;bleu!&gt;&gt;</p>"
        expected = u"&lt;&lt;sacr\N{LATIN SMALL LETTER E WITH ACUTE} bleu!&gt;&gt;".encode("utf-8")
        soup = BeautifulSoup(text)
        str = soup.p.string
        #self.assertEquals(str.encode("utf-8"), expected)


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

    def test_nonsensical_declaration(self):
        # Declarations that don't make any sense are ignored.
        self.assertSoupEquals('<! Foo = -8><p>a</p>', "<p>a</p>")

    def test_whitespace_in_doctype(self):
        # A declaration that has extra whitespace is ignored.
        self.assertSoupEquals(
            ('<! DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN">'
             '<p>foo</p>'),
            '<p>foo</p>')

    def test_incomplete_declaration(self):
        # An incomplete declaration will screw up the rest of the document.
        self.assertSoupEquals('a<!b <p>c', '<p>a</p>')

    def test_cdata_where_it_doesnt_belong(self):
        #CDATA sections are ignored.
        markup = "<div><![CDATA[foo]]>"
        self.assertSoupEquals(markup, "<div></div>")

    def test_attribute_value_never_got_closed(self):
        markup = '<a href="http://foo.com/</a> and blah and blah'
        soup = self.soup(markup)
        self.assertEquals(
            soup.a['href'], "http://foo.com/</a> and blah and blah")

    def test_attribute_value_was_closed_by_subsequent_tag(self):
        markup = """<a href="foo</a>, </a><a href="bar">baz</a>"""
        soup = self.soup(markup)
        # The string between the first and second quotes was interpreted
        # as the value of the 'href' attribute.
        self.assertEquals(soup.a['href'], 'foo</a>, </a><a href=')

        #The string after the second quote (bar"), was treated as an
        #empty attribute called bar.
        self.assertEquals(soup.a['bar'], '')
        self.assertEquals(soup.a.string, "baz")

    def test_attribute_value_with_embedded_brackets(self):
        soup = self.soup('<a b="<a>">')
        self.assertEquals(soup.a['b'], '<a>')

    def test_nonexistent_entity(self):
        soup = self.soup("<p>foo&#bar;baz</p>")
        self.assertEquals(soup.p.string, "foobar;baz")

        # Compare a real entity.
        soup = self.soup("<p>foo&#100;baz</p>")
        self.assertEquals(soup.p.string, "foodbaz")

        # Also compare html5lib, which preserves the &# before the
        # entity name.

    def test_entity_was_not_finished(self):
        soup = self.soup("<p>&lt;Hello&gt")
        # Compare html5lib, which completes the entity.
        self.assertEquals(soup.p.string, "<Hello&gt")

    def test_document_ends_with_incomplete_declaration(self):
        soup = self.soup('<p>a<!b')
        # This becomes a string 'a'. The incomplete declaration is ignored.
        # Compare html5lib, which turns it into a comment.
        self.assertEquals(soup.p.contents, ['a'])

    def test_document_starts_with_bogus_declaration(self):
        soup = self.soup('<! Foo ><p>a</p>')
        # The declaration is ignored altogether.
        self.assertEquals(soup.encode(), "<html><body><p>a</p></body></html>")

    def test_tag_name_contains_unicode(self):
        # Unicode characters in tag names are stripped.
        tag_name = u"<our\N{SNOWMAN}>Joe</our\N{SNOWMAN}>"
        self.assertSoupEquals("<our>Joe</our>")

class TestLXMLBuilderEncodingConversion(SoupTest):
    # Test Beautiful Soup's ability to decode and encode from various
    # encodings.

    def setUp(self):
        super(TestLXMLBuilderEncodingConversion, self).setUp()
        self.unicode_data = u"<html><head></head><body><foo>Sacr\N{LATIN SMALL LETTER E WITH ACUTE} bleu!</foo></body></html>"
        self.utf8_data = self.unicode_data.encode("utf-8")
        # Just so you know what it looks like.
        self.assertEqual(
            self.utf8_data,
            "<html><head></head><body><foo>Sacr\xc3\xa9 bleu!</foo></body></html>")

    def test_ascii_in_unicode_out(self):
        # ASCII input is converted to Unicode. The original_encoding
        # attribute is set.
        ascii = "<foo>a</foo>"
        soup_from_ascii = self.soup(ascii)
        unicode_output = soup_from_ascii.decode()
        self.assertTrue(isinstance(unicode_output, unicode))
        self.assertEquals(unicode_output, self.document_for(ascii))
        self.assertEquals(soup_from_ascii.original_encoding, "ascii")

    def test_unicode_in_unicode_out(self):
        # Unicode input is left alone. The original_encoding attribute
        # is not set.
        soup_from_unicode = self.soup(self.unicode_data)
        self.assertEquals(soup_from_unicode.decode(), self.unicode_data)
        self.assertEquals(soup_from_unicode.foo.string, u'Sacr\xe9 bleu!')
        self.assertEquals(soup_from_unicode.original_encoding, None)

    def test_utf8_in_unicode_out(self):
        # UTF-8 input is converted to Unicode. The original_encoding
        # attribute is set.
        soup_from_utf8 = self.soup(self.utf8_data)
        self.assertEquals(soup_from_utf8.decode(), self.unicode_data)
        self.assertEquals(soup_from_utf8.foo.string, u'Sacr\xe9 bleu!')

    def test_utf8_out(self):
        # The internal data structures can be encoded as UTF-8.
        soup_from_unicode = self.soup(self.unicode_data)
        self.assertEquals(soup_from_unicode.encode('utf-8'), self.utf8_data)

    HEBREW_DOCUMENT = '<html><head><title>Hebrew (ISO 8859-8) in Visual Directionality</title></head><body><h1>Hebrew (ISO 8859-8) in Visual Directionality</h1>\xed\xe5\xec\xf9</body></html>'

    def test_real_hebrew_document(self):
        # A real-world test to make sure we can convert ISO-8859-9 (a
        # Hebrew encoding) to UTF-8.
        soup = self.soup(self.HEBREW_DOCUMENT,
                         fromEncoding="iso-8859-8")
        self.assertEquals(soup.original_encoding, 'iso-8859-8')
        self.assertEquals(
            soup.encode('utf-8'),
            self.HEBREW_DOCUMENT.decode("iso-8859-8").encode("utf-8"))

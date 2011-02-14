from beautifulsoup.builder.html5lib_builder import HTML5TreeBuilder
from beautifulsoup.element import Comment
from test_lxml import (
    TestLXMLBuilder,
    TestLXMLBuilderInvalidMarkup,
    )

class TestHTML5Builder(TestLXMLBuilder):
    """See `BuilderSmokeTest`."""

    @property
    def default_builder(self):
        return HTML5TreeBuilder()

    def test_bare_string(self):
        # A bare string is turned into some kind of HTML document or
        # fragment recognizable as the original string.
        #
        # In this case, lxml puts a <p> tag around the bare string.
        self.assertSoupEquals(
            "A bare string", "A bare string")

    def test_correctly_nested_tables(self):
        markup = ('<table id="1">'
                  '<tr>'
                  "<td>Here's another table:"
                  '<table id="2">'
                  '<tr><td>foo</td></tr>'
                  '</table></td>')

        self.assertSoupEquals(
            markup,
            '<table id="1"><tbody><tr><td>Here\'s another table:'
            '<table id="2"><tbody><tr><td>foo</td></tr></tbody></table>'
            '</td></tr></tbody></table>')

        self.assertSoupEquals(
            "<table><thead><tr><td>Foo</td></tr></thead>"
            "<tbody><tr><td>Bar</td></tr></tbody>"
            "<tfoot><tr><td>Baz</td></tr></tfoot></table>")

    def test_collapsed_whitespace(self):
        """Whitespace is preserved even in tags that don't require it."""
        self.assertSoupEquals("<p>   </p>")
        self.assertSoupEquals("<b>   </b>")

    def test_cdata_where_its_ok(self):
        # In html5lib 0.9.0, all CDATA sections are converted into
        # comments.  In a later version (unreleased as of this
        # writing), CDATA sections in tags like <svg> and <math> will
        # be preserved. BUT, I'm not sure how Beautiful Soup needs to
        # adjust to transform this preservation into the construction
        # of a BS CData object.
        markup = "<svg><![CDATA[foobar]]>"

        # Eventually we should be able to do a find(text="foobar") and
        # get a CData object.
        self.assertSoupEquals(markup, "<svg><!--[CDATA[foobar]]--></svg>")


class TestHTML5BuilderInvalidMarkup(TestLXMLBuilderInvalidMarkup):
    """See `BuilderInvalidMarkupSmokeTest`."""

    @property
    def default_builder(self):
        return HTML5TreeBuilder()

    def test_unclosed_block_level_elements(self):
        # The unclosed <b> tag is closed so that the block-level tag
        # can be closed, and another <b> tag is inserted after the
        # next block-level tag begins.
        self.assertSoupEquals(
            '<blockquote><p><b>Foo</blockquote><p>Bar',
            '<blockquote><p><b>Foo</b></p></blockquote><p><b>Bar</b></p>')

    def test_table_containing_bare_markup(self):
        # Markup should be in table cells, not directly in the table.
        self.assertSoupEquals("<table><div>Foo</div></table>",
                              "<div>Foo</div><table></table>")

    def test_incorrectly_nested_tables(self):
        self.assertSoupEquals(
            '<table><tr><table><tr id="nested">',
            ('<table><tbody><tr></tr></tbody></table>'
             '<table><tbody><tr id="nested"></tr></tbody></table>'))

    def test_doctype_in_body(self):
        markup = "<p>one<!DOCTYPE foobar>two</p>"
        self.assertSoupEquals(markup, "<p>onetwo</p>")

    def test_cdata_where_it_doesnt_belong(self):
        # Random CDATA sections are converted into comments.
        markup = "<div><![CDATA[foo]]>"
        soup = self.soup(markup)
        data = soup.find(text="[CDATA[foo]]")
        self.assertEquals(data.__class__, Comment)

    def test_nonsensical_declaration(self):
        # Declarations that don't make any sense are turned into comments.
        soup = self.soup('<! Foo = -8><p>a</p>')
        self.assertEquals(str(soup),
                          ("<!-- Foo = -8-->"
                           "<html><head></head><body><p>a</p></body></html>"))

        soup = self.soup('<p>a</p><! Foo = -8>')
        self.assertEquals(str(soup),
                          ("<html><head></head><body><p>a</p>"
                           "<!-- Foo = -8--></body></html>"))


    def test_foo(self):
        isolatin = """<html><meta http-equiv="Content-type" content="text/html; charset=ISO-Latin-1" />Sacr\xe9 bleu!</html>"""
        soup = self.soup(isolatin)

        utf8 = isolatin.replace("ISO-Latin-1".encode(), "utf-8".encode())
        utf8 = utf8.replace("\xe9", "\xc3\xa9")

        #print soup

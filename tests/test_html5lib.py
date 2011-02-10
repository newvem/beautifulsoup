from beautifulsoup.builder.html5lib_builder import HTML5TreeBuilder
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

    def test_nested_tables(self):
        # See TestLXMLBuilder for TABLE_MARKUP_1 and
        # TABLE_MARKUP_2. They're both nested tables where the
        # top-level <table> and <tr> aren't closed. In TABLE_MARKUP_1
        # the second table is within a <td> tag. In
        # TABLE_MARKUP_2, the second table is floating inside a <tr> tag.
        #
        # html5lib adds <tbody> tags to each table. It treats
        # TABLE_MARKUP_1 as a nested table, and TABLE_MARKUP_2 as two
        # different tables.
        self.assertSoupEquals(
            self.TABLE_MARKUP_1,
            '<table id="1"><tbody>'
            "<tr><td>Here's another table:"
            '<table id="2"><tbody><tr><td>foo</td></tr></tbody></table>'
            "</td></tr></tbody></table>"
            )

        self.assertSoupEquals(
            self.TABLE_MARKUP_2,
            '<table id="1"><tbody>'
            "<tr><td>Here's another table:</td></tr>"
            '</tbody></table>'
            '<table id="2"><tbody><tr><td>foo</td></tr></tbody></table>'
            )

    def test_collapsed_whitespace(self):
        """Whitespace is preserved even in tags that don't require it."""
        self.assertSoupEquals("<p>   </p>")
        self.assertSoupEquals("<b>   </b>")


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

    def test_incorrectly_nested_tables(self):
        self.assertSoupEquals(
            '<table><tr><table><tr id="nested">',
            ('<table><tbody><tr></tr></tbody></table>'
             '<table><tbody><tr id="nested"></tr></tbody></table>'))

    def test_foo(self):
        isolatin = """<html><meta http-equiv="Content-type" content="text/html; charset=ISO-Latin-1" />Sacr\xe9 bleu!</html>"""
        soup = self.soup(isolatin)

        utf8 = isolatin.replace("ISO-Latin-1".encode(), "utf-8".encode())
        utf8 = utf8.replace("\xe9", "\xc3\xa9")

        print soup

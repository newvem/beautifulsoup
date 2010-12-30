from helpers import BuilderInvalidMarkupSmokeTest, BuilderSmokeTest
from beautifulsoup.builder.html5lib_builder import HTML5TreeBuilder


class TestHTML5Builder(BuilderSmokeTest):
    """See `BuilderSmokeTest`."""

    def setUp(self):
        self.default_builder = HTML5TreeBuilder()


class TestHTML5BuilderInvalidMarkup(BuilderInvalidMarkupSmokeTest):
    """See `BuilderInvalidMarkupSmokeTest`."""

    def setUp(self):
        self.default_builder = HTML5TreeBuilder()

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




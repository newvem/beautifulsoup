from html5lib.treebuilders.dom import dom2sax
from html5lib import treewalkers
from beautifulsoup.builder import HTMLTreeBuilder, SAXTreeBuilder
import html5lib


class HTML5TreeBuilder(SAXTreeBuilder, HTMLTreeBuilder):
    """Use html5lib to build a tree, then turn the parsed tree into
    SAX events to build a Beautiful Soup tree.

    Eventually this will be replaced with something sane.
    """

    def __init__(self):
        self.soup = None

    def feed(self, markup):
        builder = html5lib.treebuilders.getTreeBuilder("dom")
        parser = html5lib.HTMLParser(tree=builder)
        doc = parser.parse(markup)
        walker = treewalkers.getTreeWalker('dom')
        dom2sax(doc, self)

    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        return u'<html><head></head><body>%s</body></html>' % fragment


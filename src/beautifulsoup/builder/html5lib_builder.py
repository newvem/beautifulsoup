from html5lib.treebuilders.dom import dom2sax
from html5lib import treewalkers
from beautifulsoup.element import Comment
from beautifulsoup.builder import HTMLTreeBuilder, TreeBuilder
import html5lib

class SAXTreeBuilder(TreeBuilder):
    """A Beautiful Soup treebuilder that listens for SAX events."""

    def feed(self, markup):
        raise NotImplementedError()

    def close(self):
        pass

    def startElement(self, name, attrs):
        attrs = dict((key[1], value) for key, value in attrs.items())
        #print "Start %s, %r" % (name, attrs)
        self.soup.handle_starttag(name, attrs)

    def endElement(self, name):
        #print "End %s" % name
        self.soup.handle_endtag(name)

    def startElementNS(self, nsTuple, nodeName, attrs):
        # Throw away (ns, nodeName) for now.
        self.startElement(nodeName, attrs)

    def endElementNS(self, nsTuple, nodeName):
        # Throw away (ns, nodeName) for now.
        self.endElement(nodeName)
        #handler.endElementNS((ns, node.nodeName), node.nodeName)

    def startPrefixMapping(self, prefix, nodeValue):
        # Ignore the prefix for now.
        pass

    def endPrefixMapping(self, prefix):
        # Ignore the prefix for now.
        # handler.endPrefixMapping(prefix)
        pass

    def characters(self, content):
        self.soup.handle_data(content)

    def startDocument(self):
        pass

    def endDocument(self):
        pass


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



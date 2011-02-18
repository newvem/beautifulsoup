from beautifulsoup.element import Entities

__all__ = [
    'HTMLTreeBuilder',
    'SAXTreeBuilder',
    'TreeBuilder',
    ]


class TreeBuilder(Entities):
    """Turn a document into a Beautiful Soup object tree."""

    assume_html = False

    def __init__(self):
        self.soup = None

    def isSelfClosingTag(self, name):
        return name in self.self_closing_tags

    def reset(self):
        pass

    def feed(self, markup):
        raise NotImplementedError()

    def test_fragment_to_document(self, fragment):
        """Wrap an HTML fragment to make it look like a document.

        Different parsers do this differently. For instance, lxml
        introduces an empty <head> tag, and html5lib
        doesn't. Abstracting this away lets us write simple tests
        which run HTML fragments through the parser and compare the
        results against other HTML fragments.

        This method should not be used outside of tests.
        """
        return fragment


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


class HTMLTreeBuilder(TreeBuilder):
    """This TreeBuilder knows facts about HTML.

    Such as which tags are self-closing tags.
    """

    assume_html = True

    preserve_whitespace_tags = set(['pre', 'textarea'])
    self_closing_tags = set(['br' , 'hr', 'input', 'img', 'meta',
                            'spacer', 'link', 'frame', 'base'])


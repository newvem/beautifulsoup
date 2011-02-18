import re
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

    def prepare_markup(self, markup, user_specified_encoding=None,
                       document_declared_encoding=None):
        return markup, None, None

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

    def set_up_substitutions(self, tag):
        pass


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

    # Used by set_up_substitutions to detect the charset in a META tag
    CHARSET_RE = re.compile("((^|;)\s*charset=)([^;]*)", re.M)

    def set_up_substitutions(self, tag):
        if tag.name != 'meta':
            return False

        http_equiv = tag.get('http-equiv')
        content = tag.get('content')

        if (http_equiv is not None
            and content is not None
            and http_equiv.lower() == 'content-type'):
            # This is an interesting meta tag.
            match = self.CHARSET_RE.search(content)
            if match:
                if (self.soup.declared_html_encoding is not None or
                    self.soup.original_encoding == self.soup.fromEncoding):
                    # An HTML encoding was sniffed while converting
                    # the document to Unicode, or an HTML encoding was
                    # sniffed during a previous pass through the
                    # document, or an encoding was specified
                    # explicitly and it worked. Rewrite the meta tag.
                    def rewrite(match):
                        return match.group(1) + "%SOUP-ENCODING%"
                    tag['content'] = self.CHARSET_RE.sub(rewrite, content)
                    return True
                else:
                    # This is our first pass through the document.
                    # Go through it again with the encoding information.
                    new_charset = match.group(3)
                    if (new_charset is not None
                        and new_charset != self.soup.original_encoding):
                        self.soup.declared_html_encoding = new_charset
                        self.soup._feed(self.soup.declared_html_encoding)
                        raise StopParsing
                    pass
        return False

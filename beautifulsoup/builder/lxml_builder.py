from lxml import etree
from beautifulsoup.element import Comment, Doctype
from beautifulsoup.builder import TreeBuilder, HTMLTreeBuilder
from beautifulsoup.dammit import UnicodeDammit
import types

class LXMLTreeBuilderForXML(TreeBuilder):
    DEFAULT_PARSER_CLASS = etree.XMLParser

    @property
    def default_parser(self):
        # This can either return a parser object or a class, which
        # will be instantiated with default arguments.
        return etree.XMLParser

    def __init__(self, parser=None, empty_element_tags=None):
        if empty_element_tags is not None:
            self.empty_element_tags = set(empty_element_tags)
        if parser is None:
            # Use the default parser.
            parser = self.default_parser
        if callable(parser):
            # Instantiate the parser with default arguments
            parser = parser(target=self, strip_cdata=False)
        self.parser = parser
        self.soup = None

    def prepare_markup(self, markup, user_specified_encoding=None,
                       document_declared_encoding=None):
        """
        :return: A 3-tuple (markup, original encoding, encoding
        declared within markup).
        """
        if isinstance(markup, unicode):
            return markup, None, None

        try_encodings = [user_specified_encoding, document_declared_encoding]
        dammit = UnicodeDammit(markup, try_encodings, isHTML=True)
        return (dammit.markup, dammit.original_encoding,
                dammit.declared_html_encoding)

    def feed(self, markup):
        self.parser.feed(markup)
        self.parser.close()

    def close(self):
        pass

    def start(self, name, attrs):
        self.soup.handle_starttag(name, attrs)

    def end(self, name):
        self.soup.endData()
        completed_tag = self.soup.tagStack[-1]
        self.soup.handle_endtag(name)

    def pi(self, target, data):
        pass

    def data(self, content):
        self.soup.handle_data(content)

    def doctype(self, name, pubid, system):
        self.soup.endData()
        doctype = Doctype.for_name_and_ids(name, pubid, system)
        self.soup.object_was_parsed(doctype)

    def comment(self, content):
        "Handle comments as Comment objects."
        self.soup.endData()
        self.soup.handle_data(content)
        self.soup.endData(Comment)

    def test_fragment_to_document(self, fragment):
        """See `TreeBuilder`."""
        return u'<html><body>%s</body></html>' % fragment


class LXMLTreeBuilder(HTMLTreeBuilder, LXMLTreeBuilderForXML):

    @property
    def default_parser(self):
        return etree.HTMLParser

    def end(self, name):
        self.soup.handle_endtag(name)

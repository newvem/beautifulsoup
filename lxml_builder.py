from lxml import etree
from BeautifulSoup import TreeBuilder

class LXMLBuilder(TreeBuilder):

    def __init__(self, parser_class=etree.XMLParser, self_closing_tags=[]):
        self.parser = parser_class(target=self)
        self.self_closing_tags = self_closing_tags
        self.soup = None

    def isSelfClosingTag(self, name):
        return name in self.self_closing_tags

    def feed(self, markup):
        self.parser.feed(markup)
        self.parser.close()

    def start(self, name, attrs):
        self.soup.handle_starttag(name, attrs)

    def end(self, name):
        self.soup.handle_endtag(name)

    def data(self, content):
        self.soup.handle_data(content)

    def comment(self, content):
        "Handle comments as Comment objects."
        self._toStringSubclass(content, Comment)

    def _toStringSubclass(self, text, subclass):
        """Adds a certain piece of text to the tree as a NavigableString
        subclass."""
        self.soup.endData()
        self.data(text)
        self.soup.endData(subclass)

from lxml import etree
from beautifulsoup.element import Comment
from beautifulsoup.builder import TreeBuilder

class LXMLTreeBuilder(TreeBuilder):

    def __init__(self, parser_class=etree.HTMLParser, self_closing_tags=[]):
        self.parser = parser_class(target=self)
        self.self_closing_tags = self_closing_tags
        self.soup = None

    def isSelfClosingTag(self, name):
        return name in self.self_closing_tags

    def feed(self, markup):
        self.parser.feed(markup)
        self.parser.close()

    def close(self):
        pass

    def start(self, name, attrs):
        self.soup.handle_starttag(name, attrs)

    def end(self, name):
        self.soup.handle_endtag(name)

    def data(self, content):
        self.soup.handle_data(content)

    def comment(self, content):
        "Handle comments as Comment objects."
        self.soup.endData()
        self.soup.handle_data(content)
        self.soup.endData(Comment)

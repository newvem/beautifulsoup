from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
from lxml_builder import LXMLBuilder
from lxml import etree
builder = LXMLBuilder()
soup = BeautifulStoneSoup("<foo>bar</foo>", builder=builder)
print soup.prettify()

soup = BeautifulSoup("<foo>bar</foo>", builder=builder)
print soup.prettify()

builder = LXMLBuilder(parser_class=etree.HTMLParser, self_closing_tags=["br"])
soup = BeautifulSoup("<html><head><title>test<body><h1>page<script>foo<b>bar</script><br />title</h1>", builder=builder)
print soup.prettify()

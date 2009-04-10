from BeautifulSoup import BeautifulStoneSoup, BeautifulSoup
from lxml_builder import LXMLTreeBuilder
from lxml import etree
builder = LXMLTreeBuilder(parser_class=etree.XMLParser)
soup = BeautifulStoneSoup("<foo>bar</foo>", builder=builder)
print soup.prettify()

soup = BeautifulSoup("<foo>bar</foo>", builder=builder)
print soup.prettify()

builder = LXMLTreeBuilder(parser_class=etree.HTMLParser, self_closing_tags=['br'])
soup = BeautifulSoup("<html><head><title>test<body><h1>page<!--Comment--><script>foo<b>bar</script><br />title</h1>", builder=builder)
print soup.prettify()

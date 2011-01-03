# -*- coding: utf-8 -*-
"""Tests of Beautiful Soup as a whole."""

import unittest
from beautifulsoup.element import SoupStrainer
from beautifulsoup.dammit import UnicodeDammit
from beautifulsoup.testing import SoupTest


class TestEncodingConversion(SoupTest):
    # Test Beautiful Soup's ability to decode and encode from various
    # encodings.

    def setUp(self):
        super(TestEncodingConversion, self).setUp()
        self.unicode_data = u"<html><body><foo>\xe9</foo></body></html>"
        self.utf8_data = self.unicode_data.encode("utf-8")
        self.assertEqual(
            self.utf8_data, "<html><body><foo>\xc3\xa9</foo></body></html>")

    def test_ascii_in_unicode_out(self):
        # ASCII input is converted to Unicode. The originalEncoding
        # attribute is set.
        ascii = "<foo>a</foo>"
        soup_from_ascii = self.soup(ascii)
        unicode_output = soup_from_ascii.decode()
        self.assertTrue(isinstance(unicode_output, unicode))
        self.assertEquals(unicode_output, self.document_for(ascii))
        self.assertEquals(soup_from_ascii.originalEncoding, "ascii")

    def test_unicode_in_unicode_out(self):
        # Unicode input is left alone. The originalEncoding attribute
        # is not set.
        soup_from_unicode = self.soup(self.unicode_data)
        self.assertEquals(soup_from_unicode.decode(), self.unicode_data)
        self.assertEquals(soup_from_unicode.foo.string, u'\xe9')
        self.assertEquals(soup_from_unicode.originalEncoding, None)

    def test_utf8_in_unicode_out(self):
        # UTF-8 input is converted to Unicode. The originalEncoding
        # attribute is set.
        soup_from_utf8 = self.soup(self.utf8_data)
        self.assertEquals(soup_from_utf8.decode(), self.unicode_data)
        self.assertEquals(soup_from_utf8.foo.string, u'\xe9')

    def test_utf8_out(self):
        # The internal data structures can be encoded as UTF-8.
        soup_from_unicode = self.soup(self.unicode_data)
        self.assertEquals(soup_from_unicode.encode('utf-8'), self.utf8_data)

    def test_hebrew(self):
        # A real-world test to make sure we can convert ISO-8859-9 (a
        # Hebrew encoding) to UTF-8.
        iso_8859_8= '<HTML><HEAD><TITLE>Hebrew (ISO 8859-8) in Visual Directionality</TITLE></HEAD><BODY><H1>Hebrew (ISO 8859-8) in Visual Directionality</H1>\xed\xe5\xec\xf9</BODY></HTML>'
        utf8 = '<html><head><title>Hebrew (ISO 8859-8) in Visual Directionality</title></head><body><h1>Hebrew (ISO 8859-8) in Visual Directionality</h1>\xd7\x9d\xd7\x95\xd7\x9c\xd7\xa9</body></html>'
        soup = self.soup(iso_8859_8, fromEncoding="iso-8859-8")
        self.assertEquals(soup.originalEncoding, 'iso-8859-8')
        self.assertEquals(soup.encode('utf-8'), utf8)


class TestSelectiveParsing(SoupTest):

    def test_parse_with_soupstrainer(self):
        markup = "No<b>Yes</b><a>No<b>Yes <c>Yes</c></b>"
        strainer = SoupStrainer("b")
        soup = self.soup(markup, parseOnlyThese=strainer)
        self.assertEquals(soup.encode(), "<b>Yes</b><b>Yes <c>Yes</c></b>")


class TestUnicodeDammit(unittest.TestCase):
    """Standalone tests of Unicode, Dammit."""

    def test_smart_quotes_to_xml_entities(self):
        markup = "<foo>\x91\x92\x93\x94</foo>"
        dammit = UnicodeDammit(markup)
        self.assertEquals(
            dammit.unicode, "<foo>&#x2018;&#x2019;&#x201C;&#x201D;</foo>")

    def test_smart_quotes_to_html_entities(self):
        markup = "<foo>\x91\x92\x93\x94</foo>"
        dammit = UnicodeDammit(markup, smartQuotesTo="html")
        self.assertEquals(
            dammit.unicode, "<foo>&lsquo;&rsquo;&ldquo;&rdquo;</foo>")

    def test_detect_utf8(self):
        utf8 = "\xc3\xa9"
        dammit = UnicodeDammit(utf8)
        self.assertEquals(dammit.unicode, u'\xe9')
        self.assertEquals(dammit.originalEncoding, 'utf-8')

    def test_convert_hebrew(self):
        hebrew = "\xed\xe5\xec\xf9"
        dammit = UnicodeDammit(hebrew, ["iso-8859-8"])
        self.assertEquals(dammit.originalEncoding, 'iso-8859-8')
        self.assertEquals(dammit.unicode, u'\u05dd\u05d5\u05dc\u05e9')

    def test_dont_see_smart_quotes_where_there_are_none(self):
        utf_8 = "\343\202\261\343\203\274\343\202\277\343\202\244 Watch"
        dammit = UnicodeDammit(utf_8)
        self.assertEquals(dammit.originalEncoding, 'utf-8')
        self.assertEquals(dammit.unicode.encode("utf-8"), utf_8)

    def test_ignore_inappropriate_codecs(self):
        utf8_data = u"Räksmörgås".encode("utf-8")
        dammit = UnicodeDammit(utf8_data, ["iso-8859-8"])
        self.assertEquals(dammit.originalEncoding, 'utf-8')

    def test_ignore_invalid_codecs(self):
        utf8_data = u"Räksmörgås".encode("utf-8")
        for bad_encoding in ['.utf8', '...', 'utF---16.!']:
            dammit = UnicodeDammit(utf8_data, [bad_encoding])
            self.assertEquals(dammit.originalEncoding, 'utf-8')

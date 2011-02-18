# -*- coding: utf-8 -*-
"""Tests of Beautiful Soup as a whole."""

import unittest
from beautifulsoup.element import SoupStrainer
from beautifulsoup.dammit import UnicodeDammit
from beautifulsoup.testing import SoupTest


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

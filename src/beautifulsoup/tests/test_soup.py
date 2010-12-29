# -*- coding: utf-8 -*-
"""Tests of Beautiful Soup as a whole."""

import unittest
from helpers import SoupTest
from beautifulsoup.dammit import UnicodeDammit

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


class TestUnicodeDammit(unittest.TestCase):
    """Standalone tests of Unicode, Dammit."""

    def test_smart_quote_replacement(self):
        markup = "<foo>\x92</foo>"
        dammit = UnicodeDammit(markup)
        self.assertEquals(dammit.unicode, "<foo>&#x2019;</foo>")

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

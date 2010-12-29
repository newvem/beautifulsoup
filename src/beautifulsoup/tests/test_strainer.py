import unittest
from helpers import SoupTest
from beautifulsoup import BeautifulSoup
from beautifulsoup.element import SoupStrainer

class TestSoupStrainer(unittest.TestCase):

    def test_soupstrainer(self):
        strainer = SoupStrainer("b")
        soup = BeautifulSoup("A <b>bold</b> <meta /> <i>statement</i>",
                             parseOnlyThese=strainer)
        self.assertEquals(soup.decode(), "<b>bold</b>")

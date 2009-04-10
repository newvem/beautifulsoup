from treebuilder import CompatibilityTest
from beautifulsoup.builder.lxml_builder import LXMLTreeBuilder
import unittest

def additional_tests():
    return unittest.TestSuite([CompatibilityTest(LXMLTreeBuilder())])

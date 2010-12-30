# -*- coding: utf-8 -*-
"""Tests for Beautiful Soup's tree traversal methods.

The tree traversal methods are the main advantage of using Beautiful
Soup over other parsers.

Different parsers will build different Beautiful Soup trees given the
same markup, but all Beautiful Soup trees can be traversed with the
methods tested here.
"""

import re
from beautifulsoup.element import SoupStrainer
from helpers import SoupTest

class TreeTest(SoupTest):

    def assertSelects(self, tags, should_match):
        """Make sure that the given tags have the correct text.

        This is used in tests that define a bunch of tags, each
        containing a single string, and then select certain strings by
        some mechanism.
        """
        self.assertEqual([tag.string for tag in tags], should_match)

    def assertSelectsIDs(self, tags, should_match):
        """Make sure that the given tags have the correct IDs.

        This is used in tests that define a bunch of tags, each
        containing a single string, and then select certain strings by
        some mechanism.
        """
        self.assertEqual([tag['id'] for tag in tags], should_match)


class TestFind(TreeTest):
    """Basic tests of the find() method.

    find() just calls findAll() with limit=1, so it's not tested all
    that thouroughly here.
    """

    def test_find_tag(self):
        soup = self.soup("<a>1</a><b>2</b><a>3</a><b>4</b>")
        self.assertEqual(soup.find("b").string, "2")

    def test_unicode_text_find(self):
        soup = self.soup(u'<h1>Räksmörgås</h1>')
        self.assertEqual(soup.find(text=u'Räksmörgås'), u'Räksmörgås')


class TestFindAll(TreeTest):
    """Basic tests of the findAll() method."""

    def test_find_all_text_nodes(self):
        """You can search the tree for text nodes."""
        soup = self.soup("<html>Foo<b>bar</b>\xbb</html>")
        # Exact match.
        self.assertEqual(soup.findAll(text="bar"), [u"bar"])
        # Match any of a number of strings.
        self.assertEqual(
            soup.findAll(text=["Foo", "bar"]), [u"Foo", u"bar"])
        # Match a regular expression.
        self.assertEqual(soup.findAll(text=re.compile('.*')),
                         [u"Foo", u"bar", u'\xbb'])
        # Match anything.
        self.assertEqual(soup.findAll(text=True),
                         [u"Foo", u"bar", u'\xbb'])

    def test_find_all_limit(self):
        """You can limit the number of items returned by findAll."""
        soup = self.soup("<a>1</a><a>2</a><a>3</a><a>4</a><a>5</a>")
        self.assertSelects(soup.findAll('a', limit=3), ["1", "2", "3"])
        self.assertSelects(soup.findAll('a', limit=1), ["1"])
        self.assertSelects(
            soup.findAll('a', limit=10), ["1", "2", "3", "4", "5"])

        # A limit of 0 means no limit.
        self.assertSelects(
            soup.findAll('a', limit=0), ["1", "2", "3", "4", "5"])

class TestFindAllByName(TreeTest):
    """Test ways of finding tags by tag name."""

    def setUp(self):
        super(TreeTest, self).setUp()
        self.tree =  self.soup("""<a>First tag.</a>
                                  <b>Second tag.</b>
                                  <c>Third <a>Nested tag.</a> tag.</c>""")

    def test_find_all_by_tag_name(self):
        # Find all the <a> tags.
        self.assertSelects(
            self.tree.findAll('a'), ['First tag.', 'Nested tag.'])

    def test_find_all_on_non_root_element(self):
        # You can call find_all on any node, not just the root.
        self.assertSelects(self.tree.c.findAll('a'), ['Nested tag.'])

    def test_calling_element_invokes_find_all(self):
        self.assertSelects(self.tree('a'), ['First tag.', 'Nested tag.'])

    def test_find_all_by_tag_strainer(self):
        self.assertSelects(
            self.tree.findAll(SoupStrainer('a')),
            ['First tag.', 'Nested tag.'])

    def test_find_all_by_tag_names(self):
        self.assertSelects(
            self.tree.findAll(['a', 'b']),
            ['First tag.', 'Second tag.', 'Nested tag.'])

    def test_find_all_by_tag_dict(self):
        self.assertSelects(
            self.tree.findAll({'a' : True, 'b' : True}),
            ['First tag.', 'Second tag.', 'Nested tag.'])

    def test_find_all_by_tag_re(self):
        self.assertSelects(
            self.tree.findAll(re.compile('^[ab]$')),
            ['First tag.', 'Second tag.', 'Nested tag.'])

    def test_find_all_with_tags_matching_method(self):
        # You can define an oracle method that determines whether
        # a tag matches the search.
        def id_matches_name(tag):
            return tag.name == tag.get('id')

        tree = self.soup("""<a id="a">Match 1.</a>
                            <a id="1">Does not match.</a>
                            <b id="b">Match 2.</a>""")

        self.assertSelects(
            tree.findAll(id_matches_name), ["Match 1.", "Match 2."])


class TestFindAllByAttribute(TreeTest):

    def test_find_all_by_attribute_name(self):
        # You can pass in keyword arguments to findAll to search by
        # attribute.
        tree = self.soup("""
                         <a id="first">Matching a.</a>
                         <a id="second">
                          Non-matching <b id="first">Matching b.</b>a.
                         </a>""")
        self.assertSelects(tree.findAll(id='first'),
                           ["Matching a.", "Matching b."])

    def test_find_all_by_attribute_dict(self):
        # You can pass in a dictionary as the argument 'attrs'. This
        # lets you search for attributes like 'name' (a fixed argument
        # to findAll) and 'class' (a reserved word in Python.)
        tree = self.soup("""
                         <a name="name1" class="class1">Name match.</a>
                         <a name="name2" class="class2">Class match.</a>
                         <a name="name3" class="class3">Non-match.</a>
                         <name1>A tag called 'name1'.</name1>
                         """)

        # This doesn't do what you want.
        self.assertSelects(tree.findAll(name='name1'),
                           ["A tag called 'name1'."])
        # This does what you want.
        self.assertSelects(tree.findAll(attrs={'name' : 'name1'}),
                           ["Name match."])

        # Passing class='class2' would cause a syntax error.
        self.assertSelects(tree.findAll(attrs={'class' : 'class2'}),
                           ["Class match."])

    def test_find_all_by_class(self):
        # Passing in a string to 'attrs' will search the CSS class.
        tree = self.soup("""
                         <a class="1">Class 1.</a>
                         <a class="2">Class 2.</a>
                         <b class="1">Class 1.</a>
                         """)
        self.assertSelects(tree.findAll('a', '1'), ['Class 1.'])
        self.assertSelects(tree.findAll(attrs='1'), ['Class 1.', 'Class 1.'])

    def test_find_all_by_attribute_soupstrainer(self):
        tree = self.soup("""
                         <a id="first">Match.</a>
                         <a id="second">Non-match.</a>""")

        strainer = SoupStrainer(attrs={'id' : 'first'})
        self.assertSelects(tree.findAll(strainer), ['Match.'])

    def test_find_all_with_missing_atribute(self):
        # You can pass in None as the value of an attribute to findAll.
        # This will match tags that do not have that attribute set.
        tree = self.soup("""<a id="1">ID present.</a>
                            <a>No ID present.</a>
                            <a id="">ID is empty.</a>""")
        self.assertSelects(tree.findAll('a', id=None), ["No ID present."])

    def test_find_all_with_defined_attribute(self):
        # You can pass in None as the value of an attribute to findAll.
        # This will match tags that have that attribute set to any value.
        tree = self.soup("""<a id="1">ID present.</a>
                            <a>No ID present.</a>
                            <a id="">ID is empty.</a>""")
        self.assertSelects(
            tree.findAll(id=True), ["ID present.", "ID is empty."])

    def test_find_all_with_numeric_attribute(self):
        # If you search for a number, it's treated as a string.
        tree = self.soup("""<a id=1>Unquoted attribute.</a>
                            <a id="1">Quoted attribute.</a>""")

        expected = ["Unquoted attribute.", "Quoted attribute."]
        self.assertSelects(tree.findAll(id=1), expected)
        self.assertSelects(tree.findAll(id="1"), expected)

    def test_find_all_with_list_attribute_values(self):
        # You can pass a list of attribute values instead of just one,
        # and you'll get tags that match any of the values.
        tree = self.soup("""<a id="1">1</a>
                            <a id="2">2</a>
                            <a id="3">3</a>
                            <a>No ID.</a>""")
        self.assertSelects(tree.findAll(id=["1", "3", "4"]),
                           ["1", "3"])

    def test_find_all_with_regular_expression_attribute_value(self):
        # You can pass a regular expression as an attribute value, and
        # you'll get tags whose values for that attribute match the
        # regular expression.
        tree = self.soup("""<a id="a">One a.</a>
                            <a id="aa">Two as.</a>
                            <a id="ab">Mixed as and bs.</a>
                            <a id="b">One b.</a>
                            <a>No ID.</a>""")

        self.assertSelects(tree.findAll(id=re.compile("^a+$")),
                           ["One a.", "Two as."])


class TestParentOperations(TreeTest):
    """Test navigation and searching through an element's parents."""

    def setUp(self):
        super(TestParentOperations, self).setUp()
        self.tree = self.soup('''<ul id="empty"></ul>
                                 <ul id="top">
                                  <ul id="middle">
                                   <ul id="bottom">
                                    <b>Start here</b>
                                   </ul>
                                  </ul>''')
        self.start = self.tree.b


    def test_parent(self):
        self.assertEquals(self.start.parent['id'], 'bottom')
        self.assertEquals(self.start.parent.parent['id'], 'middle')
        self.assertEquals(self.start.parent.parent.parent['id'], 'top')

    def test_parent_of_top_tag_is_soup_object(self):
        top_tag = self.tree.contents[0]
        self.assertEquals(top_tag.parent, self.tree)

    def test_soup_object_has_no_parent(self):
        self.assertEquals(None, self.tree.parent)

    def test_find_parents(self):
        self.assertSelectsIDs(
            self.start.findParents('ul'), ['bottom', 'middle', 'top'])
        self.assertSelectsIDs(
            self.start.findParents('ul', id="middle"), ['middle'])

    def test_find_parent(self):
        self.assertEquals(self.start.findParent('ul')['id'], 'bottom')

    def test_parent_of_text_element(self):
        text = self.tree.find(text="Start here")
        self.assertEquals(text.parent.name, 'b')

    def test_text_element_find_parent(self):
        text = self.tree.find(text="Start here")
        self.assertEquals(text.findParent('ul')['id'], 'bottom')

    def test_parent_generator(self):
        parents = [parent['id'] for parent in self.start.parentGenerator()
                   if parent is not None and parent.has_key('id')]
        self.assertEquals(parents, ['bottom', 'middle', 'top'])


class TestNextOperations(TreeTest):

    def setUp(self):
        super(TestNextOperations, self).setUp()
        self.tree = self.soup(
            '<html id="start"><b id="1">One</b><b id="2">Two</b><b id="3">Three</b></html>')
        self.start = self.tree.b

    def test_next(self):
        self.assertEquals(self.start.next, "One")
        self.assertEquals(self.start.next.next['id'], "2")

    def test_next_of_last_item_is_none(self):
        last = self.tree.find(text="Three")
        self.assertEquals(last.next, None)

    def test_next_of_root_is_none(self):
        # The document root is outside the next/previous chain.
        self.assertEquals(self.tree.next, None)

    def test_find_all_next(self):
        self.assertSelects(self.start.findAllNext('b'), ["Two", "Three"])
        self.assertSelects(self.start.findAllNext('b', id=3), ["Three"])

    def test_find_next(self):
        self.assertEquals(self.start.findNext('b')['id'], '2')
        self.assertEquals(self.start.findNext(text="Three"), "Three")

    def test_find_next_for_text_element(self):
        text = self.tree.find(text="One")
        self.assertEquals(text.findNext("b").string, "Two")
        self.assertSelects(text.findAllNext("b"), ["Two", "Three"])

    def test_next_generator(self):
        start = self.tree.find(text="Two")
        successors = [node for node in start.nextGenerator()]
        # There are two successors: the final <b> tag and its text contents.
        # Then we go off the end.
        tag, contents, none = successors
        self.assertEquals(tag['id'], '3')
        self.assertEquals(contents, "Three")
        self.assertEquals(none, None)

        # XXX Should nextGenerator really return None? Seems like it
        # should just stop.


class TestElementObjects(SoupTest):
    """Test various features of element objects."""

    def test_len(self):
        """The length of an element is its number of children."""
        soup = self.soup("<top>1<b>2</b>3</top>")

        # The BeautifulSoup object itself contains one element: the
        # <top> tag.
        self.assertEquals(len(soup.contents), 1)
        self.assertEquals(len(soup), 1)

        # The <top> tag contains three elements: the text node "1", the
        # <b> tag, and the text node "3".
        self.assertEquals(len(soup.top), 3)
        self.assertEquals(len(soup.top.contents), 3)

    def test_member_access_invokes_find(self):
        """Accessing a Python member .foo or .fooTag invokes find('foo')"""
        soup = self.soup('<b><i></i></b>')
        self.assertEqual(soup.b, soup.find('b'))
        self.assertEqual(soup.bTag, soup.find('b'))
        self.assertEqual(soup.b.i, soup.find('b').find('i'))
        self.assertEqual(soup.bTag.iTag, soup.find('b').find('i'))
        self.assertEqual(soup.a, None)
        self.assertEqual(soup.aTag, None)

    def test_has_key(self):
        """has_key() checks for the presence of an attribute."""
        soup = self.soup("<foo attr='bar'>")
        self.assertTrue(soup.foo.has_key('attr'))
        self.assertFalse(soup.foo.has_key('attr2'))

    def test_string(self):
        # A tag that contains only a text node makes that node
        # available as .string.
        soup = self.soup("<b>foo</b>")
        self.assertEquals(soup.b.string, 'foo')

    def test_lack_of_string(self):
        """Only a tag containing a single text node has a .string."""
        soup = self.soup("<b>f<i>e</i>o</b>")
        self.assertFalse(soup.b.string)

        soup = self.soup("<b></b>")
        self.assertFalse(soup.b.string)

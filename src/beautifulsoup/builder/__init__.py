import markupbase
import re
from HTMLParser import HTMLParser, HTMLParseError
# element has taken care of import weirdness, so import name2codepoint
# from there to avoid duplicating the weirdness.
from beautifulsoup.element import name2codepoint
from beautifulsoup.element import (
    CData, Comment, Declaration, Entities, ProcessingInstruction)
from beautifulsoup.util import buildSet, isList, isString

__all__ = ['TreeBuilder',
           'HTMLParserXMLTreeBuilder',
           'HTMLParserTreeBuilder',
           'XMLTreeBuilder',
           'HTMLTreeBuilder',
           'ICantBelieveItsValidHTMLTreeBuilder']

#This hack makes the HTMLParser-based tree builders able to parse XML
#with namespaces.
markupbase._declname_match = re.compile(r'[a-zA-Z][-_.:a-zA-Z0-9]*\s*').match

def buildTagMap(default, *args):
    """Turns a list of maps, lists, or scalars into a single map.
    Used to build the nestable_tags and reset_nesting_tags maps out of
    lists and partial maps."""
    built = {}
    for portion in args:
        if hasattr(portion, 'items'):
            #It's a map. Merge it.
            for k,v in portion.items():
                built[k] = v
        elif isList(portion) and not isString(portion):
            #It's a list. Map each item to the default.
            for k in portion:
                built[k] = default
        else:
            #It's a scalar. Map it to the default.
            built[portion] = default
    return built


class TreeBuilder(Entities):

    smartQuotesTo = Entities.XML_ENTITIES
    preserve_whitespace_tags = buildSet()
    quote_tags = buildSet()
    self_closing_tags = buildSet()
    assume_html = False

    def __init__(self):
        self.soup = None

    def isSelfClosingTag(self, name):
        return name in self.self_closing_tags

    def reset(self):
        pass

    def feed(self):
        pass


class HTMLParserXMLTreeBuilder(HTMLParser, TreeBuilder):

    """
    This class defines a basic tree builder based on Python's built-in
    HTMLParser. The tree builder knows nothing about tag
    behavior except for the following:

      You can't close a tag without closing all the tags it encloses.
      That is, "<foo><bar></foo>" actually means
      "<foo><bar></bar></foo>".

    [Another possible explanation is "<foo><bar /></foo>", but unless
    you specify 'bar' in self_closing_tags, this class will never use
    that explanation.]

    This class is useful for parsing XML or made-up markup languages,
    or when BeautifulSoup makes an assumption counter to what you were
    expecting.


    HTMLParser will process most bad HTML, and the BeautifulSoup class
    has some tricks for dealing with some HTML that kills HTMLParser,
    but Beautiful Soup can nonetheless choke or lose data if your data
    uses self-closing tags or declarations incorrectly.

    This class uses regexes to sanitize input, avoiding the vast
    majority of these problems. If the problems don't apply to you,
    pass in False for markupMassage, and you'll get better
    performance.

    The default parser massage techniques fix the two most common
    instances of invalid HTML that choke HTMLParser:

        <br/> (No space between name of closing tag and tag close)
        <! --Comment--> (Extraneous whitespace in declaration)

    You can pass in a custom list of (RE object, replace method)
    tuples to get HTMLParserXMLTreeBuilder to scrub your input the way you
    want.
    """
    reset_nesting_tags = {}
    nestable_tags = {}

    MARKUP_MASSAGE = [(re.compile('(<[^<>]*)/>'),
                       lambda x: x.group(1) + ' />'),
                      (re.compile('<!\s+([^<>]*)>'),
                       lambda x: '<!' + x.group(1) + '>')
                      ]

    def __init__(self, convertEntities=None, markupMassage=True,
                 selfClosingTags=None,
                 smartQuotesTo=Entities.XML_ENTITIES):
        HTMLParser.__init__(self)
        self.soup = None
        self.convertEntities = convertEntities
        self.instanceSelfClosingTags = buildSet(selfClosingTags or [])
        self.markupMassage = markupMassage
        self.smartQuotesTo = smartQuotesTo
        self.quoteStack = []

        # Set the rules for how we'll deal with the entities we
        # encounter
        if self.convertEntities:
            # It doesn't make sense to convert encoded characters to
            # entities even while you're converting entities to Unicode.
            # Just convert it all to Unicode.
            self.smartQuotesTo = None
            if convertEntities == self.HTML_ENTITIES:
                self.convertXMLEntities = False
                self.convertHTMLEntities = True
                self.escapeUnrecognizedEntities = True
            elif convertEntities == self.XHTML_ENTITIES:
                self.convertXMLEntities = True
                self.convertHTMLEntities = True
                self.escapeUnrecognizedEntities = False
            elif convertEntities == self.XML_ENTITIES:
                self.convertXMLEntities = True
                self.convertHTMLEntities = False
                self.escapeUnrecognizedEntities = False
        else:
            self.convertXMLEntities = False
            self.convertHTMLEntities = False
            self.escapeUnrecognizedEntities = False

    def feed(self, markup):
        if markup is not None:
            if self.markupMassage:
                if not isList(self.markupMassage):
                    self.markupMassage = self.MARKUP_MASSAGE
                for fix, m in self.markupMassage:
                    markup = fix.sub(m, markup)
                # TODO: We get rid of markupMassage so that the
                # soup object can be deepcopied later on. Some
                # Python installations can't copy regexes. If anyone
                # was relying on the existence of markupMassage, this
                # might cause problems.
                # XXX: This might not be necessary now that we've moved
                # the massage code into the builder.
                #del(self.markupMassage)
        HTMLParser.feed(self, markup)

    def isSelfClosingTag(self, name):
        """Returns true iff the given string is the name of a
        self-closing tag according to this parser."""
        return (name in self.self_closing_tags
                or name in self.instanceSelfClosingTags)

    def handle_starttag(self, name, attrs):
        if len(self.quoteStack) > 0:
            #This is not a real tag.
            #print "<%s> is not real!" % name
            attrs = ''.join(map(lambda(x, y): ' %s="%s"' % (x, y), attrs))
            self.handle_data('<%s%s>' % (name, attrs))
            return
        if not self.isSelfClosingTag(name):
            self.soup.endData()
            self._smartPop(name)
        tag = self.soup.handle_starttag(name, attrs)
        if tag is None:
            # The tag was filtered out by the SoupStrainer
            return
        if name in self.quote_tags:
            #print "Beginning quote (%s)" % name
            self.quoteStack.append(name)
            self.literal = 1
        if self.isSelfClosingTag(name):
            self.soup.handle_endtag(name)

    def handle_endtag(self, name):
        if self.quoteStack and self.quoteStack[-1] != name:
            #This is not a real end tag.
            #print "</%s> is not real!" % name
            self.handle_data('</%s>' % name)
            return
        self.soup.handle_endtag(name)
        if self.quoteStack and self.quoteStack[-1] == name:
            self.quoteStack.pop()
            self.literal = (len(self.quoteStack) > 0)

    def handle_data(self, content):
        #print "Handling data " + content
        self.soup.handle_data(content)

    def handle_pi(self, text):
        """Handle a processing instruction as a ProcessingInstruction
        object, possibly one with a %SOUP-ENCODING% slot into which an
        encoding will be plugged later."""
        if text[:3] == "xml":
            text = u"xml version='1.0' encoding='%SOUP-ENCODING%'"
        self._toStringSubclass(text, ProcessingInstruction)

    def handle_comment(self, text):
        "Handle comments as Comment objects."
        self._toStringSubclass(text, Comment)

    def handle_charref(self, ref):
        "Handle character references as data."
        if self.convertEntities:
            data = unichr(int(ref))
        else:
            data = '&#%s;' % ref
        self.handle_data(data)

    def handle_entityref(self, ref):
        """Handle entity references as data, possibly converting known
        HTML and/or XML entity references to the corresponding Unicode
        characters."""
        data = None
        if self.convertHTMLEntities:
            try:
                data = unichr(name2codepoint[ref])
            except KeyError:
                pass

        if not data and self.convertXMLEntities:
                data = self.XML_ENTITIES_TO_SPECIAL_CHARS.get(ref)

        if not data and self.convertHTMLEntities and \
            not self.XML_ENTITIES_TO_SPECIAL_CHARS.get(ref):
                # TODO: We've got a problem here. We're told this is
                # an entity reference, but it's not an XML entity
                # reference or an HTML entity reference. Nonetheless,
                # the logical thing to do is to pass it through as an
                # unrecognized entity reference.
                #
                # Except: when the input is "&carol;" this function
                # will be called with input "carol". When the input is
                # "AT&T", this function will be called with input
                # "T". We have no way of knowing whether a semicolon
                # was present originally, so we don't know whether
                # this is an unknown entity or just a misplaced
                # ampersand.
                #
                # The more common case is a misplaced ampersand, so I
                # escape the ampersand and omit the trailing semicolon.
                data = "&amp;%s" % ref
        if not data:
            # This case is different from the one above, because we
            # haven't already gone through a supposedly comprehensive
            # mapping of entities to Unicode characters. We might not
            # have gone through any mapping at all. So the chances are
            # very high that this is a real entity, and not a
            # misplaced ampersand.
            data = "&%s;" % ref
        self.handle_data(data)

    def handle_decl(self, data):
        "Handle DOCTYPEs and the like as Declaration objects."
        self._toStringSubclass(data, Declaration)

    def _toStringSubclass(self, text, subclass):
        """Adds a certain piece of text to the tree as a NavigableString
        subclass."""
        self.soup.endData()
        self.handle_data(text)
        self.soup.endData(subclass)

    def _smartPop(self, name):

        """We need to pop up to the previous tag of this type, unless
        one of this tag's nesting reset triggers comes between this
        tag and the previous tag of this type, OR unless this tag is a
        generic nesting trigger and another generic nesting trigger
        comes between this tag and the previous tag of this type.

        Examples:
         <p>Foo<b>Bar *<p>* should pop to 'p', not 'b'.
         <p>Foo<table>Bar *<p>* should pop to 'table', not 'p'.
         <p>Foo<table><tr>Bar *<p>* should pop to 'tr', not 'p'.

         <li><ul><li> *<li>* should pop to 'ul', not the first 'li'.
         <tr><table><tr> *<tr>* should pop to 'table', not the first 'tr'
         <td><tr><td> *<td>* should pop to 'tr', not the first 'td'
        """

        nestingResetTriggers = self.nestable_tags.get(name)
        isNestable = nestingResetTriggers != None
        isResetNesting = self.reset_nesting_tags.has_key(name)
        popTo = None
        inclusive = True
        for i in range(len(self.soup.tagStack)-1, 0, -1):
            p = self.soup.tagStack[i]
            if (not p or p.name == name) and not isNestable:
                #Non-nestable tags get popped to the top or to their
                #last occurance.
                popTo = name
                break
            if (nestingResetTriggers != None
                and p.name in nestingResetTriggers) \
                or (nestingResetTriggers == None and isResetNesting
                    and self.reset_nesting_tags.has_key(p.name)):

                #If we encounter one of the nesting reset triggers
                #peculiar to this tag, or we encounter another tag
                #that causes nesting to reset, pop up to but not
                #including that tag.
                popTo = p.name
                inclusive = False
                break
            p = p.parent
        if popTo:
            self.soup._popToTag(popTo, inclusive)

    def parse_declaration(self, i):
        """Treat a bogus SGML declaration as raw data. Treat a CDATA
        declaration as a CData object."""
        j = None
        if self.rawdata[i:i+9] == '<![CDATA[':
             k = self.rawdata.find(']]>', i)
             if k == -1:
                 k = len(self.rawdata)
             data = self.rawdata[i+9:k]
             j = k+3
             self._toStringSubclass(data, CData)
        else:
            try:
                j = HTMLParser.parse_declaration(self, i)
            except HTMLParseError:
                toHandle = self.rawdata[i:]
                self.handle_data(toHandle)
                j = i + len(toHandle)
        return j


class HTMLParserTreeBuilder(HTMLParserXMLTreeBuilder):
    """This builder knows the following facts about HTML:

    * Some tags have no closing tag and should be interpreted as being
      closed as soon as they are encountered.

    * The text inside some tags (ie. 'script') may contain tags which
      are not really part of the document and which should be parsed
      as text, not tags. If you want to parse the text as tags, you can
      always fetch it and parse it explicitly.

    * Tag nesting rules:

      Most tags can't be nested at all. For instance, the occurance of
      a <p> tag should implicitly close the previous <p> tag.

       <p>Para1<p>Para2
        should be transformed into:
       <p>Para1</p><p>Para2

      Some tags can be nested arbitrarily. For instance, the occurance
      of a <blockquote> tag should _not_ implicitly close the previous
      <blockquote> tag.

       Alice said: <blockquote>Bob said: <blockquote>Blah
        should NOT be transformed into:
       Alice said: <blockquote>Bob said: </blockquote><blockquote>Blah

      Some tags can be nested, but the nesting is reset by the
      interposition of other tags. For instance, a <tr> tag should
      implicitly close the previous <tr> tag within the same <table>,
      but not close a <tr> tag in another table.

       <table><tr>Blah<tr>Blah
        should be transformed into:
       <table><tr>Blah</tr><tr>Blah
        but,
       <tr>Blah<table><tr>Blah
        should NOT be transformed into
       <tr>Blah<table></tr><tr>Blah

    Differing assumptions about tag nesting rules are a major source
    of problems with the BeautifulSoup class. If BeautifulSoup is not
    treating as nestable a tag your page author treats as nestable,
    try subclassing this tree builder or using another parser's tree
    builder."""

    assume_html = True
    preserve_whitespace_tags = buildSet(['pre', 'textarea'])
    quote_tags = buildSet(['script', 'textarea'])
    self_closing_tags = buildSet(['br' , 'hr', 'input', 'img', 'meta',
                                  'spacer', 'link', 'frame', 'base'])

    #According to the HTML standard, each of these inline tags can
    #contain another tag of the same type. Furthermore, it's common
    #to actually use these tags this way.
    nestable_inline_tags = ['span', 'font', 'q', 'object', 'bdo', 'sub', 'sup',
                            'center']

    #According to the HTML standard, these block tags can contain
    #another tag of the same type. Furthermore, it's common
    #to actually use these tags this way.
    nestable_block_tags = ['blockquote', 'div', 'fieldset', 'ins', 'del']

    #Lists can contain other lists, but there are restrictions.
    nestable_list_tags = { 'ol' : [],
                           'ul' : [],
                           'li' : ['ul', 'ol'],
                           'dl' : [],
                           'dd' : ['dl'],
                           'dt' : ['dl'] }

    #Tables can contain other tables, but there are restrictions.
    nestable_table_tags = {'table' : [],
                           'tr' : ['table', 'tbody', 'tfoot', 'thead'],
                           'td' : ['tr'],
                           'th' : ['tr'],
                           'thead' : ['table'],
                           'tbody' : ['table'],
                           'tfoot' : ['table'],
                           }

    non_nestable_block_tags = ['address', 'form', 'p', 'pre']

    #If one of these tags is encountered, all tags up to the next tag of
    #this type are popped.
    reset_nesting_tags = buildTagMap(None, nestable_block_tags, 'noscript',
                                     non_nestable_block_tags,
                                     nestable_list_tags,
                                     nestable_table_tags)

    nestable_tags = buildTagMap([], nestable_inline_tags, nestable_block_tags,
                                nestable_list_tags, nestable_table_tags)


    def __init__(self, *args, **kwargs):
        if not kwargs.has_key('smartQuotesTo'):
            kwargs['smartQuotesTo'] = self.HTML_ENTITIES
        HTMLParserXMLTreeBuilder.__init__(self, *args, **kwargs)

# Some aliases to use if you don't care about the underlying
# implementation.
XMLTreeBuilder = HTMLParserXMLTreeBuilder
HTMLTreeBuilder = HTMLParserTreeBuilder

class ICantBelieveItsValidHTMLTreeBuilder(HTMLParserTreeBuilder):
    """The  is oriented towards skipping over
    common HTML errors like unclosed tags. However, sometimes it makes
    errors of its own. For instance, consider this fragment:

     <b>Foo<b>Bar</b></b>

    This is perfectly valid (if bizarre) HTML. However, the
    BeautifulSoup class will implicitly close the first b tag when it
    encounters the second 'b'. It will think the author wrote
    "<b>Foo<b>Bar", and didn't close the first 'b' tag, because
    there's no real-world reason to bold something that's already
    bold. When it encounters '</b></b>' it will close two more 'b'
    tags, for a grand total of three tags closed instead of two. This
    can throw off the rest of your document structure. The same is
    true of a number of other tags, listed below.

    It's much more common for someone to forget to close a 'b' tag
    than to actually use nested 'b' tags, and the BeautifulSoup class
    handles the common case. This class handles the not-co-common
    case: where you can't believe someone wrote what they did, but
    it's valid HTML and BeautifulSoup screwed up by assuming it
    wouldn't be."""
    i_cant_believe_theyre_nestable_inline_tags = \
     ['em', 'big', 'i', 'small', 'tt', 'abbr', 'acronym', 'strong',
      'cite', 'code', 'dfn', 'kbd', 'samp', 'strong', 'var', 'b',
      'big']

    i_cant_believe_theyre_nestable_block_tags = ['noscript']

    nestable_tags = buildTagMap([], HTMLParserTreeBuilder.nestable_tags,
                                i_cant_believe_theyre_nestable_block_tags,
                                i_cant_believe_theyre_nestable_inline_tags)

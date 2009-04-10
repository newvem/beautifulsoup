"""Beautiful Soup
Elixir and Tonic
"The Screen-Scraper's Friend"
http://www.crummy.com/software/BeautifulSoup/

Beautiful Soup parses a (possibly invalid) XML or HTML document into a
tree representation. It provides methods and Pythonic idioms that make
it easy to navigate, search, and modify the tree.

A well-formed XML/HTML document yields a well-formed data
structure. An ill-formed XML/HTML document yields a correspondingly
ill-formed data structure. If your document is only locally
well-formed, you can use this library to find and process the
well-formed part of it.

Beautiful Soup works with Python 2.2 and up. It has no external
dependencies, but you'll have more success at converting data to UTF-8
if you also install these three packages:

* chardet, for auto-detecting character encodings
  http://chardet.feedparser.org/
* cjkcodecs and iconv_codec, which add more encodings to the ones supported
  by stock Python.
  http://cjkpython.i18n.org/

Beautiful Soup defines classes for two main parsing strategies:

 * BeautifulStoneSoup, for parsing XML, SGML, or your domain-specific
   language that kind of looks like XML.

 * BeautifulSoup, for parsing run-of-the-mill HTML code, be it valid
   or invalid. This class has web browser-like heuristics for
   obtaining a sensible parse tree in the face of common HTML errors.

For more than you ever wanted to know about Beautiful Soup, see the
documentation:
http://www.crummy.com/software/BeautifulSoup/documentation.html

Here, have some legalese:

Copyright (c) 2004-2009, Leonard Richardson

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

  * Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

  * Redistributions in binary form must reproduce the above
    copyright notice, this list of conditions and the following
    disclaimer in the documentation and/or other materials provided
    with the distribution.

  * Neither the name of the the Beautiful Soup Consortium and All
    Night Kosher Bakery nor the names of its contributors may be
    used to endorse or promote products derived from this software
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE, DAMMIT.

"""
from __future__ import generators

__author__ = "Leonard Richardson (leonardr@segfault.org)"
__version__ = "4.0.0"
__copyright__ = "Copyright (c) 2004-2009 Leonard Richardson"
__license__ = "New-style BSD"

__all__ = ['BeautifulSoup',

           # Stuff imported from other packages
           'Entities',
           'HTMLParserXMLTreeBuilder',
           'HTMLParserTreeBuilder',
           'HTMLTreeBuilder',
           'XMLTreeBuilder',

           'BeautifulStoneSoup',
           'ICantBelieveItsBeautifulSoup']

import re

from util import isList, isString, buildSet
from dammit import UnicodeDammit
from builder import (
    HTMLParserXMLTreeBuilder, HTMLParserTreeBuilder, HTMLTreeBuilder,
    ICantBelieveItsValidHTMLTreeBuilder, XMLTreeBuilder)
from element import Entities, NavigableString, Tag


class BeautifulStoneSoup(Tag):
    """
    This class defines the basic interface called by the tree builders.

    These methods will be called by the parser:
      reset()
      feed(markup)

    The tree builder may call these methods from its feed() implementation:
      handle_starttag(name, attrs) # See note about return value
      handle_endtag(name)
      handle_data(data) # Appends to the current data node
      endData(containerClass=NavigableString) # Ends the current data node

    No matter how complicated the underlying parser is, you should be
    able to build a tree using 'start tag' events, 'end tag' events,
    'data' events, and "done with data" events.

    If you encounter a self-closing tag, call handle_starttag and then
    handle_endtag, but note that the tag will not be displayed as a
    self-closing tag unless you also have your builder's
    isSelfClosingTag() implementation return True when passed the tag
    name.
    """
    ROOT_TAG_NAME = u'[document]'

    # Used to detect the charset in a META tag; see handleSpecialMetaTag
    CHARSET_RE = re.compile("((^|;)\s*charset=)([^;]*)", re.M)

    # Used when determining whether a text node is all whitespace and
    # can be replaced with a single space. A text node that contains
    # fancy Unicode spaces (usually non-breaking) should be left
    # alone.
    STRIP_ASCII_SPACES = { 9: None, 10: None, 12: None, 13: None, 32: None, }

    def _defaultBuilder(self):
        return HTMLParserXMLTreeBuilder()

    def __init__(self, markup="", builder=None, parseOnlyThese=None,
                 fromEncoding=None):
        """The Soup object is initialized as the 'root tag', and the
        provided markup (which can be a string or a file-like object)
        is fed into the underlying parser."""

        if builder is None:
            builder = self._defaultBuilder()
        self.builder = builder
        self.builder.soup = self

        self.parseOnlyThese = parseOnlyThese
        self.fromEncoding = fromEncoding

        self.reset()

        if hasattr(markup, 'read'):        # It's a file-type object.
            markup = markup.read()
        self.markup = markup
        try:
            self._feed(isHTML=self.builder.assume_html)
        except StopParsing:
            pass
        self.markup = None                 # The markup can now be GCed.
        self.builder.soup = None
        self.builder = None                # So can the builder.

    def _feed(self, inDocumentEncoding=None, isHTML=False):
        # Convert the document to Unicode.
        markup = self.markup
        if isinstance(markup, unicode):
            if not hasattr(self, 'originalEncoding'):
                self.originalEncoding = None
        else:
            dammit = UnicodeDammit\
                     (markup, [self.fromEncoding, inDocumentEncoding],
                      smartQuotesTo=self.builder.smartQuotesTo, isHTML=isHTML)
            markup = dammit.unicode
            self.originalEncoding = dammit.originalEncoding
            self.declaredHTMLEncoding = dammit.declaredHTMLEncoding
        self.builder.reset()

        self.builder.feed(markup)
        # Close out any unfinished strings and close all the open tags.
        self.endData()
        while self.currentTag.name != self.ROOT_TAG_NAME:
            self.popTag()

    def reset(self):
        Tag.__init__(self, self, self.builder, self.ROOT_TAG_NAME)
        self.hidden = 1
        self.builder.reset()
        self.currentData = []
        self.currentTag = None
        self.tagStack = []
        self.pushTag(self)

    def popTag(self):
        tag = self.tagStack.pop()
        # Tags with just one string-owning child get the child as a
        # 'string' property, so that soup.tag.string is shorthand for
        # soup.tag.contents[0]
        if len(self.currentTag.contents) == 1 and \
           isinstance(self.currentTag.contents[0], NavigableString):
            self.currentTag.string = self.currentTag.contents[0]

        #print "Pop", tag.name
        if self.tagStack:
            self.currentTag = self.tagStack[-1]
        return self.currentTag

    def pushTag(self, tag):
        #print "Push", tag.name
        if self.currentTag:
            self.currentTag.contents.append(tag)
        self.tagStack.append(tag)
        self.currentTag = self.tagStack[-1]

    def endData(self, containerClass=NavigableString):
        if self.currentData:
            currentData = u''.join(self.currentData)
            if (currentData.translate(self.STRIP_ASCII_SPACES) == '' and
                not buildSet([tag.name for tag in self.tagStack]).intersection(
                    self.builder.preserve_whitespace_tags)):
                if '\n' in currentData:
                    currentData = '\n'
                else:
                    currentData = ' '
            self.currentData = []
            if self.parseOnlyThese and len(self.tagStack) <= 1 and \
                   (not self.parseOnlyThese.text or \
                    not self.parseOnlyThese.search(currentData)):
                return
            o = containerClass(currentData)
            o.setup(self.currentTag, self.previous)
            if self.previous:
                self.previous.next = o
            self.previous = o
            self.currentTag.contents.append(o)


    def _popToTag(self, name, inclusivePop=True):
        """Pops the tag stack up to and including the most recent
        instance of the given tag. If inclusivePop is false, pops the tag
        stack up to but *not* including the most recent instqance of
        the given tag."""
        #print "Popping to %s" % name
        if name == self.ROOT_TAG_NAME:
            return

        numPops = 0
        mostRecentTag = None
        for i in range(len(self.tagStack)-1, 0, -1):
            if name == self.tagStack[i].name:
                numPops = len(self.tagStack)-i
                break
        if not inclusivePop:
            numPops = numPops - 1

        for i in range(0, numPops):
            mostRecentTag = self.popTag()
        return mostRecentTag

    def handle_starttag(self, name, attrs):
        """Push a start tag on to the stack.

        If this method returns None, the tag was rejected by the
        SoupStrainer. You should proceed as if the tag had not occured
        in the document. For instance, if this was a self-closing tag,
        don't call handle_endtag.
        """

        #print "Start tag %s: %s" % (name, attrs)
        self.endData()

        if (self.parseOnlyThese and len(self.tagStack) <= 1
            and (self.parseOnlyThese.text
                 or not self.parseOnlyThese.searchTag(name, attrs))):
            return None

        containsSubstitutions = False
        if name == 'meta' and self.builder.assume_html:
            containsSubstitutions = self.handleSpecialMetaTag(attrs)

        tag = Tag(self, self.builder, name, attrs, self.currentTag,
                  self.previous)
        tag.containsSubstitutions = containsSubstitutions
        if self.previous:
            self.previous.next = tag
        self.previous = tag
        self.pushTag(tag)
        return tag

    def handle_endtag(self, name):
        #print "End tag: " + name
        self.endData()
        self._popToTag(name)

    def handle_data(self, data):
        self.currentData.append(data)

    def handleSpecialMetaTag(self, attrs):
        """Beautiful Soup can detect a charset included in a META tag,
        try to convert the document to that charset, and re-parse the
        document from the beginning."""
        httpEquiv = None
        contentType = None
        contentTypeIndex = None
        tagNeedsEncodingSubstitution = False

        for i in range(0, len(attrs)):
            key, value = attrs[i]
            key = key.lower()
            if key == 'http-equiv':
                httpEquiv = value
            elif key == 'content':
                contentType = value
                contentTypeIndex = i

        if httpEquiv and contentType: # It's an interesting meta tag.
            match = self.CHARSET_RE.search(contentType)
            if match:
                if (self.declaredHTMLEncoding is not None or
                    self.originalEncoding == self.fromEncoding):
                    # An HTML encoding was sniffed while converting
                    # the document to Unicode, or an HTML encoding was
                    # sniffed during a previous pass through the
                    # document, or an encoding was specified
                    # explicitly and it worked. Rewrite the meta tag.
                    def rewrite(match):
                        return match.group(1) + "%SOUP-ENCODING%"
                    newAttr = self.CHARSET_RE.sub(rewrite, contentType)
                    attrs[contentTypeIndex] = (attrs[contentTypeIndex][0],
                                               newAttr)
                    tagNeedsEncodingSubstitution = True
                else:
                    # This is our first pass through the document.
                    # Go through it again with the encoding information.
                    newCharset = match.group(3)
                    if newCharset and newCharset != self.originalEncoding:
                        self.declaredHTMLEncoding = newCharset
                        self._feed(self.declaredHTMLEncoding)
                        raise StopParsing
                    pass
        return tagNeedsEncodingSubstitution


class BeautifulSoup(BeautifulStoneSoup):
    """A convenience class for parsing HTML without creating a builder."""
    def _defaultBuilder(self):
        return HTMLParserTreeBuilder()


class StopParsing(Exception):
    pass


class ICantBelieveItsBeautifulSoup(BeautifulStoneSoup):
    def _defaultBuilder(self):
        return ICantBelieveItsValidHTMLBuilder()


#By default, act as an HTML pretty-printer.
if __name__ == '__main__':
    import sys
    soup = BeautifulSoup(sys.stdin)
    print soup.prettify()

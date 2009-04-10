Introduction
============

  >>> from beautifulsoup import BeautifulSoup
  >>> soup = BeautifulSoup("<p>Some<b>bad<i>HTML")
  >>> print soup.prettify()
  <p>
   Some
   <b>
    bad
    <i>
     HTML
    </i>
   </b>
  </p>

  >>> soup.find(text="bad")
  u'bad'

  >>> soup.i
  <i>HTML</i>


Python 3
========

The canonical version of Beautiful Soup is the Python 2 version. You
can generate the Python 3 version by running to3.sh, or by doing what
to3.sh does: run 2to3 on BeautifulSoup.py and BeautifulSoupTests.py,
then applying the appropriate .3.diff file to each generated script.

The testall.sh script tests both the Python 2 version and a freshly
generated Python 3 version.

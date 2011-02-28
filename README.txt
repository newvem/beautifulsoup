= About Beautiful Soup 4 =

Earlier versions of Beautiful Soup included a custom HTML
parser. Beautiful Soup 4 uses Python's default HTMLParser, which does
fairly poorly on real-world HTML. By installing lxml or html5lib you
can get more accurate parsing and possibly better performance as well.

= Introduction =

  >>> from bs4 import BeautifulSoup
  >>> soup = BeautifulSoup("<p>Some<b>bad<i>HTML")
  >>> print soup.prettify()
  <html>
   <body>
    <p>
     Some
     <b>
      bad
      <i>
       HTML
      </i>
     </b>
    </p>
   </body>
  </html>
  >>> soup.find(text="bad")
  u'bad'

  >>> soup.i
  <i>HTML</i>



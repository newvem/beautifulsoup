= About Beautiful Soup 4 =

Earlier versions of Beautiful Soup included a custom HTML
parser. Beautiful Soup 4 does not include a parser. You'll need to
install either lxml or html5lib.

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



from beautifulsoup.element import Entities

__all__ = ['TreeBuilder',
           'HTMLTreeBuilder',
           ]

class TreeBuilder(Entities):
    """Turn a document into a Beautiful Soup object tree."""

    assume_html = False
    smart_quotes_to = Entities.XML_ENTITIES

    def __init__(self):
        self.soup = None
        self.self_closing_tags = set()
        self.preserve_whitespace_tags = set()

    def isSelfClosingTag(self, name):
        return name in self.self_closing_tags

    def reset(self):
        pass

    def feed(self, markup):
        raise NotImplementedError()


class HTMLTreeBuilder(TreeBuilder):
    """This TreeBuilder knows facts about HTML.

    Such as which tags are self-closing tags.
    """

    assume_html = True
    smart_quotes_to = Entities.HTML_ENTITIES

    preserve_whitespace_tags = set(['pre', 'textarea'])
    self_closing_tags = set(['br' , 'hr', 'input', 'img', 'meta',
                            'spacer', 'link', 'frame', 'base'])


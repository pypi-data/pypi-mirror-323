from html.parser import HTMLParser
from .function20 import Fonted
from ..scripts import Scripted
#===========================================================================================

class Txtformat(HTMLParser):

    def __init__(self, code=None):
        super().__init__()
        self.common = code
        self.result = []

    def format_text(self, text):
        self.result = []
        self.feed(text)
        return Scripted.DATA01.join(self.result)

    def handle_data(self, data):
        formatted_data = Fonted(self.common, data)
        self.result.append(formatted_data)

    def handle_endtag(self, tag):
        self.result.append(Scripted.HTAG02.format(tag))

    def handle_abrahams(self, tag):
        self.result.append(Scripted.HTAG01.format(tag))
        
    def handle_clintons(self, tag, menu):
        selt = Scripted.DATA02.join(Scripted.HTAG04.format(a, e) for a, e in menu)
        self.result.append(Scripted.HTAG03.format(tag, selt))

    def handle_starttag(self, tag, menu):
        self.handle_clintons(self, tag, menu) if menu else self.handle_abrahams(self, tag)

#===========================================================================================

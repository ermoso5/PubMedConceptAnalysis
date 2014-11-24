
__author__ = 'Zara'

import ner

class Adeptner:

    def __init__(self):
        self.tagger = ner.SocketNER(host='localhost', port=9191)

    def getTerms(self, text):
        return self.tagger.get_entities(text)

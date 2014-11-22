##### ADEPT NER

#p = Popen("new 2.bat", cwd=r"C:\Users\Zara\Desktop")
#stdout, stderr = p.communicate()
#print(p.returncode) # is 0 if success

import ner


__author__ = 'Zara'


class Adeptner:

    def __init__(self):
        self.tagger = ner.SocketNER(host='localhost', port=9191)

    def getTerms(self, text):
        return self.tagger.get_entities(text)

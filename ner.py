__author__ = 'Zara'


##### ADEPT NER

#p = Popen("new 2.bat", cwd=r"C:\Users\Zara\Desktop")
#stdout, stderr = p.communicate()
#print(p.returncode) # is 0 if success

import ner

class ADEPTNER:
    def __init__(self):
        self.tagger = ner.SocketNER(host='localhost', port=9191)

    def getTerms(self, str):
        return self.tagger.get_entities(str)
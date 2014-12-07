import ner
import requests
import json

__author__ = ['Zara', 'Marcello']


class Adeptner:

    def __init__(self):   
        try:
            self.tagger = ner.SocketNER(host='localhost', port=9191)
            self.testServer()     
        
        except ConnectionRefusedError:
            print("WARNING: connection to NER local server refused!")
                
        except:
            print("WARNING: the local NER doesn't work properly!")
             

    def getTerms(self, text):
        """Gets entities out of a string. It uses a local NER server"""
        return self.tagger.get_entities(text)
        
                    
    def testServer(self):
        """Test the local server and raise the exception if it doesn't return medical terms"""
        testString = "This string contains medical terms like analysis, disease and blood pressure."
        testTerms = self.getTerms(testString)
        if not testTerms:
            raise Exception



import ner
import requests

__author__ = ['Zara', 'Marcello']


class Adeptner:

    def __init__(self):
        self.ner_online = False     
        try:
            self.tagger = ner.SocketNER(host='localhost', port=9191)
            self.testServer()     
        
        except ConnectionRefusedError:
            print("WARNING: connection to NER local server refused!")
            self.ner_online = True
                
        except:
            print("WARNING: the local NER doesn't work properly!")
            self.ner_online = True
             

    def getTerms(self, string):
        """Gets entities out of a string. It uses a local NER server or default to an online NER """
        if self.ner_online == 'online':
            ADEPT_url="http://dust.stanford.edu:8080/ADEPTRest/rest/annotate"
            payload = {"adeptifyThis" : text}
            r=requests.post(ADEPT_url, data=payload)
            data = json.loads(r.text)
            result = []
            for row in data[0]["tokens"]:
                if row["label"] == "MEDTERM":
                    result.append(row["token"])
                    #print(row["token"])
            return result
        else:  
            return self.tagger.get_entities(string)
        
                    
    def testServer(self):
        """Test the local server and raise the exception if it doesn't return medical terms"""
        testString = "This string contains medical terms like analysis, disease and blood pressure."
        testTerms = self.getTerms(testString)
        if not testTerms:
            raise Exception



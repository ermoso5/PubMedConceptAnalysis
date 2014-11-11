from preprocessor import Preprocessor
from data import Parser
from graph import Graph

DEBUG = True

def main():
   
    #parsing
    par = Parser("corpus/output")
    par.split(filename="C:/Users/Zara/Downloads/corpus_1980_1985.txt")
    
    #preprocessing
    pp = Preprocessor()
    pp.processFolder(root="corpus", 
                     target="processed", 
                     stemming='heavy', 
                     min_word_length=8, 
                     remove_duplicates=True, 
                     remove_numbers=True,
                     ner=True)
    
    #create graph here
    g = Graph(graph_name="graph1")
    g.makeFromFolder(root="processed")
    
    #debug 
    if DEBUG:
        g.testGraph()
    
 
if __name__=="__main__":
    main()


# import requests
#
# ADEPT_url="http://dust.stanford.edu:8080/ADEPTRest/rest/annotate"
# textToADEPTify="PY: Im 53 and never had asthma in my life.however ive developed a very mucousy nose and a productive cough with white and yellow mucous."
# payload = {"adeptifyThis" : textToADEPTify}
#
# r=requests.post(ADEPT_url, data=payload)
# print r.text

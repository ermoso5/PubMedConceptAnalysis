import os

from preprocessor import Preprocessor
from data import Parser
from graph import Graph

DEBUG = True

def main():
   
    corpus_file = os.path.join("corpus", "test_corpus.txt")
   
    #parsing
    par = Parser("corpus")
    par.split(filename=corpus_file)
    
    #preprocessing
    pp = Preprocessor()
    pp.processFolder(root="corpus", 
                     target="processed", 
                     stemming='light', 
                     min_word_length=5, 
                     remove_duplicates=True, 
                     remove_numbers=True,
                     ner=False)
    
    #create graph here
    g = Graph(graph_name="graph1")
    g.makeFromFolder(root="processed")
    
    #debug 
    if DEBUG:
        g.testGraph()
    
 
if __name__=="__main__":
    main()


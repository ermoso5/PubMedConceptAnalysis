from preprocessor import Preprocessor
from data import Parser
from graph import Graph

DEBUG = True

def main():
   
    #parsing
    par = Parser()
    par.split(filename="corpus/test_corpus.txt")
    
    #preprocessing
    pp = Preprocessor()
    pp.processFolder(root="corpus", 
                     target="processed", 
                     stemming='heavy', 
                     min_word_length=8, 
                     remove_duplicates=True, 
                     remove_numbers=True)

    #named entity recognition goes here
    #TODO
    
    #create graph here
    g = Graph(graph_name="graph1")
    g.makeFromFolder(root="processed")
    
    #debug 
    if DEBUG:
        g.testGraph()
    
 
if __name__=="__main__":
    main()

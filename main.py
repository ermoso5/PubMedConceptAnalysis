import time

from dataparser import Parser
from preprocessor import Preprocessor
from graph import Graph

DEBUG = True

def main(parsing=True, preprocessing=True, graph_from_folder=None):
       
    #STEP 1: parsing
    if parsing:
        start = time.process_time()
        par = Parser(outputdir="corpus")     
        par.splitMedline(filename="small_medline.txt")
        print("done in {0}s".format(time.process_time()-start))
        
        
    #STEP 2: preprocessing & building the graph
    if preprocessing:
        start = time.process_time()
        g = Graph(graph_name="graph1")
        pp = Preprocessor()
        pp.processFolder(root="corpus", 
                         graph=g,               #pass the graph object
                         target_folder=None,    #don't store intermediate files #"processed"
                         ner=True,
                         stemming='heavy', 
                         min_word_length=5, 
                         remove_duplicates=True, 
                         remove_numbers=True)
        print("done in {0}s".format(time.process_time()-start))
        if DEBUG:
            g.testGraph()
    
    
    #If needed you can build the graph from a folder
    if graph_from_folder:
        start = time.process_time()
        g.makeFromFolder(root=graph_from_folder)
        print("done in {0}s".format(time.process_time()-start))

     
if __name__=="__main__":
    main()


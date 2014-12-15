import time

from dataparser import Parser
from processor import Processor
from graph import Graph

DEBUG = True

def main(parsing=False, processing=False, finalize=True):
       
    g = Graph(graph_name="graph")
       
    #STEP 1: parsing
    if parsing:
        start = time.process_time()
        par = Parser(outputdir="corpus")     
        par.splitMedline(filename="verybigmed.txt") #verybigmed.txt
        print("Parsing done in {0}s".format(time.process_time()-start))
        
        
    #STEP 2: preprocessing & building the graph
    if processing:
        start = time.process_time()
        pp = Processor()
        pp.folderToGraph(root="corpus",
                         graph=g,               #pass the graph object
                         target_folder=None,    #don't store intermediate files #"processed"
                         ner=True,
                         lemmatize=True,        #False,
                         stemming=None,         #'heavy', 
                         min_word_length=5)
        print("Processsing done in {0}s".format(time.process_time()-start))
        
        
    #STEP 3: finalization
    if finalize:
        start = time.process_time()
        g.compressTables()
        g.createFilteredView(percentage=5)
        g.normalizeWeights()
        print("Finalization done in {0}s".format(time.process_time()-start))


    if DEBUG:
        g.testGraph()

     
if __name__=="__main__":
    main()


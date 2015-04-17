import time

from dataparser import Parser
from processor import Processor
from graph import Graph

DEBUG = True

def main(parsing=False, processing=False, finalize=True):
       
    """
    Download dataset in MEDLINE format here:
    http://www.ncbi.nlm.nih.gov/pubmed/?term=%28%28%221975/01/01%22%5BPDAT%5D%20:%20%222010/01/01%22%5BPDAT%5D%29%20AND%20hasabstract%5BAll%20Fields%5D%29%20AND%20%22publication%20type%20category%22%5BPublication%20Type%5D%20AND%20%28Journal%20Article%5Bptyp%5D%20AND%20hasabstract%5Btext%5D%20AND%20%22humans%22%5BMeSH%20Terms%5D%20AND%20English%5Blang%5D%20AND%20jsubsetaim%5Btext%5D%29
    
    Warning: Processing and Finalization takes quite some time!
    """  
       
    g = Graph(graph_name="nlp")  #"nlp"
       
    #STEP 1: parsing
    if parsing:
        start = time.process_time()
        par = Parser(outputdir="corpus")  
        par.splitMedline(filename="big_medline.txt")  #  pubmed_result.txt"
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
        g.finalize(filter_top=1000) #1500
        g.normalizeWeights()
        print("Finalization done in {0}s".format(time.process_time()-start))


    #STEP 4: debug
    if DEBUG:
        g.testGraph()

     
if __name__=="__main__":
    main()


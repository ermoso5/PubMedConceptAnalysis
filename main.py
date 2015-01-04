import time

from dataparser import Parser
from processor import Processor
from graph import Graph
from analysis import Analysis

DEBUG = True

def main(parsing=False, processing=False, finalize=False, analysis=True):
       
    g = Graph(graph_name="graph")
       
    #STEP 1: parsing
    if parsing:
        start = time.process_time()
        par = Parser(outputdir="corpus")     
        #par.splitMedline(filename="verybigmed.txt") #verybigmed.txt
        par.splitMedline(filename="small_medline.txt") #verybigmed.txt
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


    #STEP 4: analysis
    if analysis:
        #concept1_source = 'benzodiazepine receptor sensitivity' #just exampleID
        #concept2_target = 'cancer'

        concept1_source = 'chronic' #just exampleID
        concept2_target = 'therapy'

        an = Analysis(g)
        path_cosine_sim, length_cosine_sim = an.a_star(
            an.getIdFromConcept(concept1_source)[0][0],
            an.getIdFromConcept(concept2_target)[0][0], similarity = 'cosine')
        path_kl_sim, length_kl_sim = an.a_star(
            an.getIdFromConcept(concept1_source)[0][0],
            an.getIdFromConcept(concept2_target)[0][0], similarity = 'kl')

        print("Using Cosine Similarity :")
        print('Path from {0} to {1}:'.format(concept1_source,concept2_target))
        print(path_cosine_sim)
        print('Path length:{}'.format(length_cosine_sim))

        print("Using Kl Similarity :")
        print('Path from {0} to {1}:'.format(concept1_source,concept2_target))
        print(path_kl_sim)
        print('Path length:{}'.format(length_kl_sim))
        #IndexError: list index out of range -> the concept is not in the graph
        #networkx.exception.NetworkXNoPath: Node 3 not reachable from 9

    if DEBUG:
        g.testGraph()

     
if __name__=="__main__":
    main()


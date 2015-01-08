import time
import networkx

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
        #concept1_source = 'angle' #'chronic' #just exampleID
        #concept2_target = 'diagnostic procedure' #'therapy'
        print("\nAnalysis : ")
        an = Analysis(g)
        print("Creating digraph ...")
        an.create_networkx_graph()
        concept1_source = ""
        concept2_target = ""
        while concept1_source != 'q' and concept2_target != 'q':
            concept1_source = input('\nInput source concept?:[Enter "q" to quit]')
            concept2_target = input('Input target concept?: [Enter "q" to quit]')
            try:
                concept = 1
                path_cosine_dis, length_cosine_dist = an.a_star(
                    an.getIdFromConcept(concept1_source),
                    an.getIdFromConcept(concept2_target), distance = 'cosine')
                concept = 2
                path_kl_dis, length_kl_dis = an.a_star(
                    an.getIdFromConcept(concept1_source),
                    an.getIdFromConcept(concept2_target), distance = 'kl')

                print("Using Cosine Distance:")
                print('\tPath from {0} to {1}: {2}'.format(concept1_source,concept2_target, path_cosine_dis))
                print('\t\t'+an.print_path(path_cosine_dis))
                print('\tPath length:{}'.format(length_cosine_dist))

                print("Using Kl Distance:")
                print('\tPath from {0} to {1}:{2}'.format(concept1_source,concept2_target, path_kl_dis))
                print('\t\t'+an.print_path(path_kl_dis))
                print('\tPath length:{}'.format(length_kl_dis))
                #IndexError: list index out of range -> the concept is not in the graph
                #networkx.exception.NetworkXNoPath: Node 3 not reachable from 9
            except IndexError:
                #make sure source and taget exist to avoid searching the whole graph
                if concept == 1:
                    print("Source '{0}' is not in the graph or doesn't have outgoing edges.".format(concept1_source))
                if concept == 2:
                    print("Target '{0}' is not in the graph or doesn't have incoming edges.".format(concept2_target))
            except networkx.exception.NetworkXNoPath:
                print("There is no path between the two nodes.")



    if DEBUG:
        g.testGraph()

     
if __name__=="__main__":
    main()


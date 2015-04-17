import time

from graph import Graph
from analysis import Analysis

def main(tests=True):

    g = Graph(graph_name="nlp")  #nlp
    if not g:
        print("ERROR: graph '{0}' doesn't exist!".format(graph_name))
    an = Analysis(g)
    print("Nodes: {0}\nEdges: {1}".format(an.nxG.number_of_nodes(), an.nxG.number_of_edges()))
     
    if tests:
        #1
        print("\n* * * Statistics about the graph * * * ")
        print("Relevant nodes: {0}".format(an.getNumRelevantNodes()))
        print("Relevant edges: {0}".format(an.getNumRelevantEdges()))
        input('Press a key to proceed...')
         
        #2
        print("\n* * * Term frequencies * * *")
        an.plotZipf(n=50)
        input('Press a key to proceed...')
        
        #3 
        print("\n* * * Compare time series of 5 randomly sampled concepts * * *")
        sampleConcepts = an.getSampleConcepts(n=5, returnName=True)
        an.plotTimeSeries(sampleConcepts, from_string=True)
        input('Press a key to proceed...')
        
        #4 
        print("\n* * * List of the 25 strongest edges in the graph * * *")
        strongEdges = an.getStrongEdges(n=25)
        for e in strongEdges:
            print("{0} > {1} [{2}]".format(e[0], e[1], e[2]))
        input('Press a key to proceed...')
    
        #5
        #print("\n* * * Test optimism of heuristic functions * * *")
        #sampleConcepts = an.getSampleConcepts(n=3, returnName=False)
        #print(sampleConcepts)
        #an.test_best_optimistic_function(sampleConcepts)
    
    
    print("\n$ @ # ANALYSIS OF DISTANCES # @ $")
    an.path_analysis()
    

     
if __name__=="__main__":
    main()


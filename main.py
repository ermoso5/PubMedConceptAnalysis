import time

from graph import Graph
from analysis import Analysis

def main():

    g = Graph(graph_name="nlp")
    if not g:
        print("ERROR: graph '{0}' doesn't exist!".format(graph_name))
    an = Analysis(g)
      
    #1
    #print("Statistics about the corpus")
    #print("Relevant nodes: {0}".format(an.getNumRelevantNodes()))
    #print("Relevant edges: {0}".format(an.getNumRelevantEdges()))
    #input('\nPress a key to proceed...')
     
    #2
    print("Zipf law of the 1st 50 concepts")
    an.plotZipf(n=50)
    input('\nPress a key to proceed...')
    
    #3 
    print("Compare time series of 5 randomly sampled concepts")
    sampleConcepts = an.getSampleConcepts(n=5, returnName=True)
    an.plotTimeSeries(sampleConcepts, from_string=True) #FIX ANALYSIS
    input('\nPress a key to proceed...')
    
    #4 
    print("List of the 25 strongest edges in the graph")
    strongEdges = an.getStrongEdges(n=25)
    for e in strongEdges:
        print("{0} > {1} [{2}]".format(e[0], e[1], e[2]))
    input('\nPress a key to proceed...')
    
    #5
    #source: try 'angle', 'chronic' 
    #target: try 'diagnostic procedure', 'therapy'
    print("\nAnalysis of distances between concepts")
    an.path_analysis()

     
if __name__=="__main__":
    main()


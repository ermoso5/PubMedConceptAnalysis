import time

from graph import Graph
from analysis import Analysis

def main():
       
    g = Graph(graph_name="nlp")
    if not g:
        print("ERROR: graph '{0}' doesn't exist!".format(graph_name)) 
    an = Analysis(g)
      
    #1
    print("Statistics about the corpus")
    print("Relevant nodes: {0}".format(an.getNumRelevantNodes()))
    print("Relevant edges: {0}".format(an.getNumRelevantEdges()))
        
    input('\nPress a key to proceed...')
     
    #2
    print("Zipf law of the 1st 50 concepts")
    an.plotZipf(n=50)
    input('\nPress a key to proceed...')
     
    #3 
    print("Compare time series of 5 randomly sampled concepts")
    sampleConcepts = an.getSampleConcepts(n=5, returnName=True)
    an.plotTimeSeries(sampleConcepts, from_string=False) #FIX ANALYSIS
    input('\nPress a key to proceed...')
    
    #4 
    print("List of the 25 strongest edges in the graph")
    an.getStrongEdges(n=25)
    input('\nPress a key to proceed...')
    
    #5
    #source: try 'angle', 'chronic' 
    #target: try 'diagnostic procedure', 'therapy'
    print("\nAnalysis of distances between concepts")
    an.create_networkx_graph()
    an.path_analysis()

    """
    def getSampleConcepts(self, n, returnName=False):
        query = ""SELECT term FROM {0} b JOIN {1} n ON b.node1=n.id 
                ORDER BY RAND() LIMIT 0, {2}"" \
                .format(self.graph.bigraph_norm, self.graph.graph_nodes, n)
        return self.graph.sendQuery(query)
     
    res = g.sendQuery(" SELECT node, sum(weight) as weight FROM ( SELECT node1 as node, sum(weight) as weight FROM nlp_weights GROUP BY node1  UNION SELECT node2 as node, sum(weight) as weight FROM nlp_weights GROUP BY node2 ) GROUP BY node ORDER BY weight DESC")
    """
     
if __name__=="__main__":
    main()


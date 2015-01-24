import time

from graph import Graph
from analysis import Analysis

def main():

    g = Graph(graph_name="nlp")

    if not g:
        print("ERROR: graph '{0}' doesn't exist!".format(graph_name))

    #concept1_source = 'angle' #'chronic' #just exampleID
    #concept2_target = 'diagnostic procedure' #'therapy'
    print("\nAnalysis : ")
    an = Analysis(g)
    an.create_networkx_graph()
    an.path_analysis()

if __name__=="__main__":
    main()


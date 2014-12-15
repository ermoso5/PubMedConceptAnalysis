import matplotlib.pyplot as plt

__author__ = "Marcello Benedetti"
__status__ = "Prototype"

DEBUG = False

class FastQueries(object):

    def __init__(self, graph):
        self.graph = graph
      
    
    def getIdFromConcept(self, concept):
        query = "SELECT id FROM {0} WHERE term LIKE '{1}'" \
                .format(self.graph.graph_nodes, concept)  
        return self.graph.sendQuery(query) 
    
    
    def getNumRelevantNodes(self):
        query = "SELECT count(*) FROM {0}" \
                .format(self.graph.filtered_nodes_view)  
        return self.graph.sendQuery(query)


    def getNumRelevantEdges(self):
        query = "SELECT count(*) FROM {0}" \
                .format(self.graph.filtered_edges_view)  
        return self.graph.sendQuery(query)


    def getTopTerms(self, n):
        query = """SELECT n.term, sum(t.frequency) as occurrences 
                   FROM {0} t JOIN {1} n ON t.id = n.id 
                   GROUP BY n.term 
                   ORDER BY occurrences DESC 
                   LIMIT {2}""" \
                .format(self.graph.time_series, self.graph.graph_nodes, n)  
        return self.graph.sendQuery(query)


    def getTimeSeries(self, concept, plot):
        query = "SELECT t.year, t.frequency FROM {0} t JOIN {1} n ON t.id=n.id WHERE n.term='{2}' ORDER BY t.year ASC" \
                .format(self.graph.time_series, self.graph.graph_nodes, concept)
        result = self.graph.sendQuery(query)
        if plot and len(result)>0:
            plt.plot([i[0] for i in result], [i[1] for i in result], 'r-o', linewidth=1.0, label=concept)
            plt.legend()
            plt.show()
        return result


    def getStrongEdges(self, n):
        query = """SELECT n1.term, n2.term, weight 
                   FROM {0} b JOIN {1} n1 ON b.node1=n1.id JOIN {1} n2 ON b.node2=n2.id  
                   ORDER BY weight DESC 
                   LIMIT {2}""" \
                .format(self.graph.bigraph_norm, self.graph.graph_nodes, n)
        return self.graph.sendQuery(query)
  

#if __name__=="__main__":
#    debug()

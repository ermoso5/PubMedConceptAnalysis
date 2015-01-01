import math
import networkx as nx
import scipy.stats as stats
import matplotlib.pyplot as plt

__author__ = ["Falitokiniaina Rabearison", "Zara Alaverdyan", "Marcello Benedetti"]

DEBUG = True

class Analysis:

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


    def a_star(self, source, target):
        weighted_oriented_edges = []
        query = "SELECT * FROM {0}".format(self.graph.bigraph_norm)
        result = self.graph.sendQuery(query)
        for row in result:
            row = (row[0], row[1], 1/float(row[2]))
            weighted_oriented_edges.append(row)
        #weighted_oriented_edges = [[int(y) for y in x] for x in weighted_oriented_edges]    #convert str into int
        #print(weighted_oriented_edges)
        nxG = nx.DiGraph()
        nxG.add_weighted_edges_from(weighted_oriented_edges)
        path = nx.astar_path(nxG, source, target, heuristic = self.heuristicFunction)
        length = nx.astar_path_length(nxG, source,target, heuristic = self.heuristicFunction)
        return path, length


    def heuristicFunction(self, concept1, concept2):
        return 1.0 / float(1e-10 + self.klSimilarity(concept1, concept2))
        #return 1.0 / float(1e-10 + self.cosineSimilarity(concept1, concept2))


    def cosineSimilarity(self, concept1, concept2):
        query1 = "SELECT year, frequency FROM {0} WHERE id= {1} ORDER BY YEAR ASC".format(self.graph.time_series, concept1)
        query2 = "SELECT year, frequency FROM {0} WHERE id= {1} ORDER BY YEAR ASC".format(self.graph.time_series, concept2)      
        concept1_time_series = self.graph.sendQuery(query1)
        concept2_time_series = self.graph.sendQuery(query2)     
        i = j = 0
        sim = 0
        norm_concept1 = 0
        norm_concept2 = 0
        while i < len(concept1_time_series) and j < len(concept2_time_series):
            year1 = concept1_time_series[i][0]
            year2 = concept2_time_series[j][0]
            freq_concept1 = concept1_time_series[i][1]
            freq_concept2 = concept2_time_series[j][1]
            if year1 == year2:
                sim += freq_concept1 * freq_concept2
                norm_concept1 += math.pow(freq_concept1, 2)
                norm_concept2 += math.pow(freq_concept2, 2)
                i += 1
                j += 1
            elif year1 > year2:
                norm_concept2 += math.pow(freq_concept2, 2)
                j += 1
            else:
                norm_concept1 += math.pow(freq_concept1, 2)
                i += 1
        while i < len(concept1_time_series):
            norm_concept1 += math.pow(concept1_time_series[i][1], 2)
            i += 1
        while j < len(concept2_time_series):
            norm_concept2 += math.pow(concept2_time_series[j][1], 2)
            j += 1
        return sim/(math.sqrt(norm_concept1 * norm_concept2))
       
        
    def klSimilarity(self, concept1, concept2):
        query1 = "SELECT year, frequency FROM {0} WHERE id= {1} ORDER BY YEAR ASC".format(self.graph.time_series, concept1)
        query2 = "SELECT year, frequency FROM {0} WHERE id= {1} ORDER BY YEAR ASC".format(self.graph.time_series, concept2)      
        concept1_time_series = self.graph.sendQuery(query1)
        concept2_time_series = self.graph.sendQuery(query2)
        c1 = []
        c2 = []
        i = j = 0
        while i < len(concept1_time_series) and j < len(concept2_time_series):
            year1 = concept1_time_series[i][0]
            year2 = concept2_time_series[j][0]
            freq_concept1 = concept1_time_series[i][1] + 1 #smoothing
            freq_concept2 = concept2_time_series[j][1] + 1
            if year1 == year2:
                c1.append(freq_concept1)
                c2.append(freq_concept2)
                i += 1
                j += 1
            elif year1 > year2:
                c1.append(1)
                c2.append(freq_concept2)
                j += 1
            elif year2 > year1:
                c1.append(freq_concept1)
                c2.append(1)           
                i += 1
        #print(c1) #print(c2)
        return 1 - stats.entropy(c1, c2)

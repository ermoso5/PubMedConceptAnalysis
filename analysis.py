import networkx as nx
from scipy.stats import entropy
from scipy.spatial.distance import cosine 
import matplotlib.pyplot as plt

__author__ = ["Falitokiniaina Rabearison", "Zara Alaverdyan", "Marcello Benedetti"]

DEBUG = True

class Analysis:

    def __init__(self, graph):
        self.graph = graph

    
    def getIdFromConcept(self, concept):
        query = "SELECT id FROM {0} WHERE term LIKE '{1}'" \
                .format(self.graph.graph_nodes, concept)  
        return self.graph.sendQuery(query)[0][0]
    
    
    def getConceptFromId(self, id):
        query = "SELECT term FROM {0} WHERE id={1}" \
                .format(self.graph.graph_nodes, id)  
        return self.graph.sendQuery(query)[0][0]
    
    
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


    def getTimeSeries(self, concept, from_string=False, plot=False):
        concept_id = self.getIdFromConcept(concept) if from_string else int(concept)
        query = "SELECT year, frequency FROM {0} WHERE id={1} ORDER BY YEAR ASC" \
                .format(self.graph.time_series, concept_id)
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


    def create_networkx_graph(self):
        weighted_oriented_edges = []
        query = "SELECT * FROM {0}".format(self.graph.bigraph_norm)
        result = self.graph.sendQuery(query)
        for row in result:
            row = (int(row[0]), int(row[1]), float(row[2]))
            weighted_oriented_edges.append(row)
        self.nxG = nx.DiGraph()
        self.nxG.add_weighted_edges_from(weighted_oriented_edges)

    def a_star(self, source, target, distance='cosine'):
        if distance == 'cosine':
            heuristic = self.heuristicFunctionCosine
        elif distance == 'kl':
            heuristic = self.heuristicFunctionKl
        path = nx.astar_path(self.nxG, source, target, heuristic)
        length = sum(self.nxG[u][v].get('weight', 1) for u, v in zip(path[:-1], path[1:]))
        return path, length


    def heuristicFunctionCosine(self, concept1, concept2):
        return self.timeSeriesDistance(concept1, concept2, type='cosine')


    def heuristicFunctionKl(self, concept1, concept2):
        dist = self.timeSeriesDistance(concept1, concept2, type='kl')
        #print(concept1, " ", concept2, " ", dist)
        return dist
        #return self.timeSeriesDistance(concept1, concept2, type='kl')

    def print_path(self,id_concepts_path_tab):
        concept_path = ""
        for concept_id in id_concepts_path_tab:
            concept_path = concept_path + " -> " + self.getConceptFromId(concept_id)
        return concept_path
 
    def timeSeriesDistance(self, concept1, concept2, type):
        concept1_time_series = self.getTimeSeries(concept1, from_string=False)
        concept2_time_series = self.getTimeSeries(concept2, from_string=False)
        i = 0
        j = 0
        c1 = []
        c2 = []
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
        #print(c1) 
        #print(c2)
        if len(c1)==0 or len(c2)==0:
            return 1 
        elif type=='cosine':
            return cosine(c1, c2)
        elif type=='kl':
            return entropy(c1, c2)
        else:
           print("Distance type not specified or unknown.")
           quit()

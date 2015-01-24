import networkx as nx
import numpy as np
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
        if len(self.graph.sendQuery(query))>0:
            return self.graph.sendQuery(query)[0][0]
        else:
            return None
    
    
    def getConceptFromId(self, id): 
        query = "SELECT term FROM {0} WHERE id={1}" \
                .format(self.graph.graph_nodes, id)
        if len(self.graph.sendQuery(query))>0:
            return self.graph.sendQuery(query)[0][0]
        else:
            return None
    
    
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

    
    def plotZipf(self, n):
        topTerms = self.getTopTerms(n)
        if len(topTerms)<1:
            return
        idx = np.arange(len(topTerms))
        labels = [i[0] for i in topTerms]
        values = [i[1] for i in topTerms]
        plt.bar(idx, values, width=0.5, align="center")
        plt.xlim([0, max(idx)])
        plt.ylim([0, max(values)+1000])
        plt.ylabel("Frequency")
        plt.title("Zipf's Law")
        plt.xticks(idx, labels, rotation=90)
        plt.tight_layout        
        plt.show()


    def getTotalFrequenciesPerYear(self):
        query = "SELECT year, sum(frequency) AS tot FROM {0} GROUP BY year ORDER BY year ASC" \
                .format(self.graph.time_series)
        return self.graph.sendQuery(query)


    def getTimeSeries(self, concept, from_string=False):
        concept_id = self.getIdFromConcept(concept) if from_string else int(concept)
        if not concept_id:
            return []
        query = "SELECT year, frequency FROM {0} WHERE id={1} ORDER BY YEAR ASC" \
                .format(self.graph.time_series, concept_id)
        tmp = dict(self.graph.sendQuery(query))
        totals = self.getTotalFrequenciesPerYear()
        result = []
        for (year, total) in totals:
            value = tmp.get(year)
            if value:
                result.append((year, value/total))
            else:
                result.append((year, 0))
        return result
        
    
    def plotTimeSeries(self, concepts, from_string=False, plot=False):
        time_series = []
        for conc in concepts:
            time_series = self.getTimeSeries(conc, from_string)
            #if plot and len(result)>0:
            plt.plot([i[0] for i in time_series], [i[1] for i in time_series], linewidth=1.0, label=conc)
        plt.ylabel("Year")
        plt.ylabel("Percentage of Total Publications (%)")
        plt.title("Usage of Terms Over Time")
        plt.tight_layout()
        plt.legend()
        plt.show()


    def getStrongEdges(self, n):
        query = """SELECT n1.term, n2.term, weight 
                   FROM {0} b JOIN {1} n1 ON b.node1=n1.id JOIN {1} n2 ON b.node2=n2.id  
                   ORDER BY weight DESC 
                   LIMIT {2}""" \
                .format(self.graph.bigraph_norm, self.graph.graph_nodes, n)
        return self.graph.sendQuery(query)


    def create_networkx_graph(self):
        print("Creating digraph ...")
        weighted_oriented_edges = []
        query = "SELECT * FROM {0}".format(self.graph.bigraph_norm)
        result = self.graph.sendQuery(query)
        for row in result:
            row = (int(row[0]), int(row[1]), float(row[2]))
            weighted_oriented_edges.append(row)
        self.nxG = nx.DiGraph()
        self.nxG.add_weighted_edges_from(weighted_oriented_edges)
        print("digraph created")


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

    def path_analysis(self):
        concept1_source = ""
        concept2_target = ""
        while concept1_source != 'q' and concept2_target != 'q':
            try:
                #make sure source and taget exist to avoid searching the whole graph
                concept = 1
                concept1_source = input('\nInput source concept?:[Enter "q" to quit]')
                source = self.getIdFromConcept(concept1_source) # if raise IndexError -> not in the initial graph
                # check if in the bi_graph
                check1 = "SELECT count(*) FROM {0} WHERE node1={1}".format(self.graph.bigraph_norm, source)
                if self.graph.sendQuery(check1)[0][0]==0:
                    raise KeyError("Source '{0}' is not in the graph or doesn't have outgoing edges.".format(concept1_source))

                concept = 2
                concept2_target = input('Input target concept?: [Enter "q" to quit]')
                target = self.getIdFromConcept(concept2_target) # if raise IndexError -> not in the initial graph
                check2 = "SELECT count(*) FROM {0} WHERE node2={1}".format(self.graph.bigraph_norm, target)
                if self.graph.sendQuery(check2)[0][0]==0:
                    raise KeyError("Target '{0}' is not in the graph or doesn't have incoming edges.".format(concept2_target))
                #END make sure source and taget exist to avoid searching the whole graph

                path_cosine_dis, length_cosine_dist = self.a_star(source, target, distance = 'cosine')
                path_kl_dis, length_kl_dis = self.a_star(source, target, distance = 'kl')

                print("Using Cosine Distance:")
                print('\tPath from {0} to {1}: {2}'.format(concept1_source,concept2_target, path_cosine_dis))
                print('\t\t'+self.print_path(path_cosine_dis))
                print('\tPath length:{}'.format(length_cosine_dist))

                print("Using Kl Distance:")
                print('\tPath from {0} to {1}:{2}'.format(concept1_source,concept2_target, path_kl_dis))
                print('\t\t'+self.print_path(path_kl_dis))
                print('\tPath length:{}'.format(length_kl_dis))
                #IndexError: list index out of range -> the concept is not in the graph
                #networkx.exception.NetworkXNoPath: Node 3 not reachable from 9
                '''
                Input source concept?:[Enter "q" to quit]acute myocardial infarction
                Input target concept?: [Enter "q" to quit]induce efficient
                Using Cosine Distance:
                    Path from acute myocardial infarction to induce efficient: [4925, 5555, 6715, 7900]
                         -> acute myocardial infarction -> recurrent -> influenza -> induce efficient
                    Path length:0.02661107195990917
                Using Kl Distance:
                    Path from acute myocardial infarction to induce efficient:[4925, 5555, 6715, 7900]
                         -> acute myocardial infarction -> recurrent -> influenza -> induce efficient
                    Path length:0.02661107195990917
                '''
            except IndexError:
                if concept == 1:
                    print("Source '{0}' is not in the initial graph.".format(concept1_source))
                if concept == 2:
                    print("Target '{0}' is not in the initial graph.".format(concept2_target))
            except nx.exception.NetworkXNoPath:
                print("There is no path between the two nodes.")
            except KeyError as Error_msg:
                print(Error_msg)

     def test_best_optimistic_function(self,list_couples):#[['565', '575'], ['1215', '245'], ['1740', '245']]
    #return best heuristic, the one with min error rate
        nb_opt_cosine_error = 0
        nb_opt_kl_error = 0
        for couple in list_couples:
            print("optimistic testing {0}".format(couple))
            real_dist_cos = nx.astar_path_length(self.nxG, couple[0], couple[1], heuristic='cosine')
            real_dist_kl = nx.astar_path_length(self.nxG, couple[0], couple[1], heuristic='kl')
            cosine_dist = self.heuristicFunctionCosine(couple[0], couple[1])
            kl_dist = self.heuristicFunctionKl(couple[0], couple[1])
            if cosine_dist > real_dist_cos:
                nb_opt_cosine_error += 1
            if kl_dist > real_dist_kl:
                nb_opt_kl_error +=1
        error_rate_cosine = nb_opt_cosine_error/len(list_couples)
        error_rate_KL = nb_opt_kl_error/len(list_couples)
        print("Optimistic COSINE heuristic ERROR : {0}".format(error_rate_cosine))
        print("Optimistic KL heuristic ERROR : {0}".format(error_rate_KL))
        if error_rate_cosine < error_rate_KL:
            return "cosine"
        else:
            return "kl"
 
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
            return abs(cosine(c1, c2))
        elif type=='kl':
            return abs(entropy(c1, c2))
        else:
           print("Distance type not specified or unknown.")
           quit()

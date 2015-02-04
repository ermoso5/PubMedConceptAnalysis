import itertools
import time
import networkx as nx
import numpy as np
from scipy.stats import entropy
from scipy.spatial.distance import cosine
import matplotlib as mpl
import matplotlib.pyplot as plt

__author__ = ["Marcello Benedetti", "Falitokiniaina Rabearison", "Zara Alaverdyan"]

DEBUG = False

class Analysis:

    def __init__(self, graph):
        print("...initializataion")
        self.graph = graph
        self.time_series_norm = self.getTimeSeriesAggregate()
        self.nxG = self.create_networkx_graph()
        print("bidirected normalized graph created in memory!")

    
    def create_networkx_graph(self):
        weighted_oriented_edges = []
        query = "SELECT * FROM {0}".format(self.graph.bigraph_norm)
        result = self.graph.sendQuery(query)
        for row in result:
            row = (int(row[0]), int(row[1]), 1-float(row[2]))  #TEST HERE
            weighted_oriented_edges.append(row)
        nxG = nx.DiGraph()
        nxG.add_weighted_edges_from(weighted_oriented_edges)
        return nxG
    
    
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
        query = "SELECT COUNT(node1) FROM ( SELECT DISTINCT node1 FROM {0} )" \
                .format(self.graph.bigraph_norm)  
        return self.graph.sendQuery(query)


    def getNumRelevantEdges(self):
        query = "SELECT count(*) FROM {0}" \
                .format(self.graph.bigraph_norm)  
        return self.graph.sendQuery(query)


    def getTopTerms(self, n):
        query = """SELECT n.term, sum(tts.frequency) freq FROM {0} tts, {1} n
                   WHERE tts.id=n.id GROUP BY term
                   ORDER BY freq DESC
                   LIMIT {2}""" \
                   .format(self.graph.time_series, self.graph.graph_nodes, n)
        return self.graph.sendQuery(query)
    
    
    def getSampleConcepts(self, n, returnName=False):
        query = """SELECT node1 FROM {0} 
                   WHERE node1 >= (abs(random()) % (SELECT max(node1) FROM {0}))
                   LIMIT 0, {1}""" \
                .format(self.graph.bigraph_norm, n)
        res = self.graph.sendQuery(query)
        if returnName:
            return [self.getConceptFromId(x[0]) for x in res] 
        return [x[0] for x in res]
        
     
    def plotZipf(self, n):
        topTerms = self.getTopTerms(n)
        if len(topTerms)<1:
            return
        idx = np.arange(len(topTerms))
        labels = [i[0] for i in topTerms]
        values = [i[1] for i in topTerms]
        plt.bar(idx, values, width=0.5, align="center")
        plt.xlim([0, max(idx)])
        plt.ylim([0, max(values)])
        plt.ylabel("Frequency")
        plt.title("Top {0} terms".format(n))
        plt.xticks(idx, labels, rotation=90)
        plt.tight_layout
        plt.show()


    def getTimeSeriesAggregate(self):
        query = "SELECT year, sum(frequency) FROM {0} GROUP BY year" \
                .format(self.graph.time_series)
        return dict(self.graph.sendQuery(query))


    def getTimeSeries(self, concept, from_string=False):
        concept_id = self.getIdFromConcept(concept) if from_string else int(concept)
        if not concept_id:
            return []
        query = "SELECT year, frequency FROM {0} WHERE id={1} ORDER BY YEAR ASC" \
                .format(self.graph.time_series, concept_id)
        result = self.graph.sendQuery(query)
        ts = []
        for i in result:
            ts.append((i[0], i[1]/self.time_series_norm.get(i[0]))) 
        return ts
    
    
    def plotTimeSeries(self, concepts, from_string=False):
        time_series = []
        for conc in concepts:
            time_series = self.getTimeSeries(conc, from_string)
            plt.plot([i[0] for i in time_series], [i[1] for i in time_series], linewidth=1.0, label=conc)
        plt.ylabel("Year")
        plt.ylabel("Percentage of Total Publications (%)")
        plt.title("Usage of Terms Over Time")
        plt.tight_layout()
        plt.legend()
        plt.show()


    def getStrongEdges(self, n):
        query = """SELECT n1.term, n2.term, b.weight 
                   FROM {0} b JOIN {1} n1 ON b.node1=n1.id JOIN {1} n2 ON b.node2=n2.id  
                   ORDER BY weight DESC 
                   LIMIT {2}""" \
                .format(self.graph.bigraph_norm, self.graph.graph_nodes, n)
        return self.graph.sendQuery(query)


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
        return dist


    def print_path(self,id_concepts_path_tab):
        concept_path = ""
        for concept_id in id_concepts_path_tab:
            concept_path = concept_path + "--> {0} ({1}) ".format(self.getConceptFromId(concept_id), concept_id)
        return concept_path


    def path_analysis(self):
        concept1_source = ""
        concept2_target = ""
        while concept1_source != 'q' and concept2_target != 'q':
            try:
                #make sure source and taget exist to avoid searching the whole graph
                concept = 1
                concept1_source = input('\nInput source concept?:[Enter "q" to quit]')
                if concept1_source=='q':
                    exit(0)

                source = self.getIdFromConcept(concept1_source) # if raise IndexError -> not in the initial graph
                # check if in the bi_graph
                check1 = "SELECT count(*) FROM {0} WHERE node1={1}".format(self.graph.bigraph_norm, source)
                r1 = self.graph.sendQuery(check1)
                if not r1 or r1[0][0]==0:
                    raise KeyError("Source '{0}' is not in the graph or doesn't have outgoing edges.".format(concept1_source))
                
                concept = 2
                concept2_target = input('Input target concept?: [Enter "q" to quit]')
                if r1[0][0]=='q':
                    exit(0)
                target = self.getIdFromConcept(concept2_target) # if raise IndexError -> not in the initial graph
                check2 = "SELECT count(*) FROM {0} WHERE node2={1}".format(self.graph.bigraph_norm, target)
                r2 = self.graph.sendQuery(check2)
                if not r2 or r2[0][0]==0:
                    raise KeyError("Target '{0}' is not in the graph or doesn't have incoming edges.".format(concept2_target))
                #END make sure source and taget exist to avoid searching the whole graph

                start = time.process_time()
                path_cosine_dis, length_cosine_dist = self.a_star(source, target, distance = 'cosine')
                print("Cosine done in {0}s".format(time.process_time()-start))
                
                start = time.process_time()
                path_kl_dis, length_kl_dis = self.a_star(source, target, distance = 'kl')
                print("KL done in {0}s".format(time.process_time()-start))
                
                start = time.process_time()
                real_dist = nx.shortest_path(self.nxG, source, target, weight='weight')
                print("Shortest path done in {0}s".format(time.process_time()-start))
                
                print("* * * PATHS * * * ")
                
                print("\nHeuristic: Cosine Distance")
                print(self.print_path(path_cosine_dis))
                print('Total length:{}'.format(length_cosine_dist))

                print("\nHeuristic: KL Divergence:")
                print(self.print_path(path_kl_dis))
                print('Total length:{}'.format(length_kl_dis))
                
                print("\nReal Path:")
                print(real_dist)
                
            except IndexError:
                if concept == 1:
                    print("Source '{0}' is not in the initial graph.".format(concept1_source))
                if concept == 2:
                    print("Target '{0}' is not in the initial graph.".format(concept2_target))
            except nx.exception.NetworkXNoPath:
                print("There is no path between the two nodes.")
            except KeyError as Error_msg:
                print(Error_msg)


    ###TO FIX
    def test_best_optimistic_function(self, listNodes):
        #return best heuristic, the one with min error rate
        #check all nodes in the graph:
        found = False
        for i in listNodes:
            found = self.check_id_in_graph(i)
            if not found:
                return False

        nb_opt_cosine_error = 0
        nb_opt_kl_error = 0
        i = 0
        for couple in itertools.combinations(listNodes,2):
            print("Couple {0}: ".format(i))
            print(couple)
            path_cosine_dis, length_cosine_dist = self.a_star(couple[0], couple[1], distance = 'cosine')
            path_kl_dis, length_kl_dis = self.a_star(couple[0], couple[1], distance = 'kl')
            real_dist = nx.shortest_path_length(self.nxG, int(couple[0]), int(couple[1]), weight='weight')
            print("path cosine : {0} \n\t"
                  "-> distance with cosine heuristic = {1}\n\t"
                  "-> real shortest distance = {2}".format(path_cosine_dis, length_cosine_dist, real_dist))
            print("path kl : {0} \n\t"
                  "-> distance with kl heuristic = {1}\n\t"
                  "-> real shortest distance = {2}".format(path_kl_dis, length_kl_dis, real_dist))
            cosine_dist = self.heuristicFunctionCosine(int(couple[0]), int(couple[1]))
            kl_dist = self.heuristicFunctionKl(int(couple[0]), int(couple[1]))
            if cosine_dist > real_dist:
                nb_opt_cosine_error += 1
            if kl_dist > real_dist:
                nb_opt_kl_error +=1
            i+=1
        error_rate_cosine = nb_opt_cosine_error/len(listNodes)
        error_rate_KL = nb_opt_kl_error/len(listNodes)
        print("COSINE heuristic ERROR : {0}".format(error_rate_cosine))
        print("KL heuristic ERROR : {0}".format(error_rate_KL))
        if error_rate_cosine < error_rate_KL:
            return "cosine"
        else:
            return "kl"
    ###
    

    def check_id_in_graph(self,id):
        found = True
        check = "SELECT count(*) FROM {0} WHERE node2={1}".format(self.graph.bigraph_norm, id)
        if not self.graph.sendQuery(check):
            print("'{0}' is not in the graph or doesn't have incoming edges.".format(id))
            found = False
        return found
 
 
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
            freq_concept1 = concept1_time_series[i][1]
            freq_concept2 = concept2_time_series[j][1]
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
            c = abs(cosine(c1, c2))
            #print(concept1, " / ", concept2, " ", c)
            return c
        elif type=='kl':
            return abs(entropy(c1, c2))
        else:
           print("Distance type not specified or unknown.")
           quit()
